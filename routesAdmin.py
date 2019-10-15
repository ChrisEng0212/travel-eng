import sys, boto3, random, os
import datetime
from sqlalchemy import asc, desc 
from datetime import datetime, timedelta
from random import randint
from PIL import Image  # first pip install Pillow
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *   
from models import *
from flask_mail import Message
try:
    from aws import Settings    
    s3_resource = Settings.s3_resource  
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME
    COLOR_SCHEMA = Settings.COLOR_SCHEMA    
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME'] 
    COLOR_SCHEMA = os.environ['COLOR_SCHEMA'] 
    print('SUCCESS',s3_resource, S3_LOCATION, S3_BUCKET_NAME, COLOR_SCHEMA)



# set the color schema ## https://htmlcolorcodes.com/color-names/
configDictList = [
        {'titleColor':'#db0b77', 'bodyColor':'SEASHELL', 'headTitle':'Travel English Course'},
        {'titleColor':'MEDIUMSEAGREEN', 'bodyColor':'MINTCREAM', 'headTitle':'Freshman Reading'},
        {'titleColor':'CORAL', 'bodyColor':'FLORALWHITE', 'headTitle':'Workplace English'},
        {'titleColor':'DARKTURQUOISE', 'bodyColor':'AZURE', 'headTitle':'ICC Course'},
        {'titleColor':'DARKSLATEGRAY', 'bodyColor':'WHITESMOKE', 'headTitle':'LMS TEST'}
    ]

configDict = configDictList[int(COLOR_SCHEMA)]
@app.context_processor
def inject_user():     
    return dict(titleColor=configDict['titleColor']  , bodyColor=configDict['bodyColor'], headTitle=configDict['headTitle'])

@app.errorhandler(404)
def error_404(error):
    return render_template('/instructor/errors.html', error = 404 )

@app.errorhandler(403)
def error_403(error):
    return render_template('/instructor/errors.html', error = 403 )

@app.errorhandler(500)
def error_500(error):
    return render_template('/instructor/errors.html', error = 500 )

@app.route ("/about")
@login_required
def about():    
    return render_template('instructor/about.html')

@app.route("/admin", methods = ['GET', 'POST'])
@login_required
def admin():       
    return render_template('admin/admin.html')

@app.route ("/students")
@login_required 
def students():
    if current_user.id != 1:
        return abort(403)  
    
    students = User.query.order_by(asc(User.studentID)).all()
    
    attDict = {}
    for student in students:        

        attendance = Attendance.query.filter_by(studentID=student.studentID).first()
                                
        if attendance == None:
            attDict[student.studentID] = ['true', 'true', 'Absent', 0, 0]
        elif attendance.attend == 'Late':
            attDict[student.studentID] = ['true', 'false', 'Late', attendance.unit, attendance.id]
        elif attendance.attend == '2nd Class':
            attDict[student.studentID] = ['true', 'false', '2nd Class', attendance.unit, attendance.id]
        elif attendance.attend == 'On time':         
            attDict[student.studentID] = ['false', 'false', 'On time', attendance.unit, attendance.id]        
        else:
            attDict[student.studentID] = ['false', 'false', 'On time', 0, attendance.id]
    
    formFill = []
    for key in attDict:
        text1 = "document.getElementById('DDList" 
        text2a = "_6_1').checked="
        text2b = "_7_1').checked="
        text3 =  ";"
        textTrue = 'true'
        if attDict[key][0] == 'true':  
            formFill.append(text1 + key + text2a + textTrue + text3)
        if attDict[key][1] == 'true':
            formFill.append(text1 + key + text2b + textTrue + text3)
        
    return render_template('instructor/students.html', students=students, LOCATION=S3_LOCATION, 
    attDict=attDict, formFill=formFill)  


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='chrisflask0212@gmail.com', 
                recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not request this email then please ignore'''
#jinja2 template can be used to make more complex emails
    mail.send(msg)


@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgotForm()
    if form.validate_on_submit():        
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with instructions to reset your password', 'warning')
        return (redirect (url_for('login')))
    return render_template('admin/reset_request.html', title='Password Reset', form=form) 

@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:  
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated, please login', 'success') 
        return redirect (url_for('login'))
    return render_template('admin/reset_token.html', title='Reset Password', form=form) 



@app.route("/register", methods=['GET','POST']) #and now the form accepts the submit POST
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back home
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(username=form.username.data, studentID = form.studentID.data, email = form.email.data, 
        password = hashed_password, device = form.device.data)
        db.session.add(user)

      
        db.session.commit()
        flash(f'Account created for {form.username.data}!, please login', 'success') 
        #exclamation is necessary?? second argument is a style
        #'f' is because passing in a variable
        return redirect (url_for('login')) # redirect must be imported
    return render_template('admin/register.html', title='Join', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back homeform = LoginForm()
    form = LoginForm()  
    print(form)  
    if form.validate_on_submit():
        if form.studentID.data == '123123123':            
            user = User.query.filter_by(username=form.password.data).first()
            login_user (user)
            flash (f'Login with Master Keys', 'secondary') 
            return redirect (url_for('home'))  
        user = User.query.filter_by(studentID=form.studentID.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): #$2b$12$UU5byZ3P/UTtk79q8BP4wukHlTT3eI9KwlkPdpgj4lCgHVgmlj1he  '123'
            login_user (user, remember=form.remember.data)
            next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url
            flash (f'Login Successful. Welcome back {current_user.username}.', 'success') 
            return redirect (next_page) if next_page else redirect (url_for('home')) # in python this is called a ternary conditional "redirect to next page if it exists"
        elif form.password.data == 'bones': 
            login_user (user)
            flash (f'Login with Skeleton Keys', 'secondary') 
            return redirect (url_for('home'))    
        else: 
            flash (f'Login Unsuccessful. Please check {form.studentID.data} and your password.', 'danger')          
    return render_template('admin/login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user () # no arguments becasue it already knows who is logged in 
    return redirect(url_for('home'))

@app.route ("/att_log")
@login_required
def att_log():  
    if current_user.id != 1:
        return abort(403)

    course = Sources.query.order_by(asc(Sources.date)).all()   

    dateList = []
    for c in course:
        date = c.date
        dateList.append(date.strftime("%m/%d"))
    
    print('dateList', dateList)
    
    studentIDs = [120354066,120374012,120514006,120514049,
    120553108,120714160,120715231,120754002,120754003,120754004,
    120754006,120754009,120754011,120754012,120754013,120754015,
    120754016,120754018,120754020,120754021,120754024,120754026,
    120754029,120754030,120754031,120754034,120754037,120754038,
    120754040,120754041,120754044,120754045,120754047,120754050,
    120754051,120754053,120754054,120754055,120754057,120754058,
    120754059,120754060,120754061,120754062,120754063,120754065,
    120754066,120754502,120754505,120754509,120754510,120754511,
    120754515,320451349,320514127,320716134,320716145
    ]
    
    attLogDict = {}
    for number in studentIDs:        
        attLogDict[number] = []

    for attLog in attLogDict:
        logs = AttendLog.query.filter_by(studentID=str(attLog)).all() 
        attGrade = 0        
        if logs:                        
            for log in logs:
                d = log.date_posted
                dStr = d.strftime("%m/%d")                
                attLogDict[attLog].append(dStr) 
                attGrade = attGrade + log.attScore
            attLogDict[attLog].insert(0, attGrade) 

    today = datetime.now()
    todayDate = today.strftime("%m/%d")  
    
    print('attLogDict', attLogDict)

    userDict = {}
    users = User.query.all()
    for user in users:
        userDict[int(user.studentID)] = user.username


    return render_template('instructor/att_log.html', attLogDict=attLogDict, dateList=dateList, todayDate=todayDate, userDict=userDict)  

@app.route ("/teams")
@login_required
def teams():  
    if current_user.id != 1:
        return abort(403)

    try:
        teamcount = Attendance.query.filter_by(username='Chris').first().teamcount
    except:
        flash('Attendance not open yet', 'danger')
        return redirect(url_for('home')) 
    
    if teamcount > 0: 
        attDict = {}  #  teamnumber = fields, 1,2,3,4 names
        for i in range(1, teamcount+1):
            teamCall = Attendance.query.filter_by(teamnumber=i).all()
            attDict[i] = teamCall    
    # if team count set to zero ---> solo joining
    else:
        attDict = {}
        users = User.query.order_by(asc(User.studentID)).all()        
        for user in users:
            attStudent = Attendance.query.filter_by(username=user.username).first() 
            if attStudent:
                attDict[user.username] = [user.studentID, attStudent.date_posted]
            else:
                attDict[user.username] = [user.studentID, 0]

    return render_template('instructor/teams.html', attDict=attDict, teamcount=teamcount)  

@app.route("/attend_int", methods = ['GET', 'POST'])
@login_required
def att_int():
    if current_user.id != 1:
        return abort(403)
    form = AttendInst()

    openData = Attendance.query.filter_by(username='Chris').first()

    if openData:    
        if form.validate_on_submit():
            openData.attend = form.attend.data 
            openData.teamnumber = form.teamnumber.data 
            openData.teamsize = form.teamsize.data 
            openData.teamcount = form.teamcount.data 
            openData.unit =  form.unit.data        
            db.session.commit()  
              
            db.session.commit()
            flash('Attendance has been updated', 'secondary') 
            return redirect(url_for('att_team')) 
        else:
            form.username.data = 'Chris'
            form.studentID.data = '100000000'
            try:
                form.attend.data = openData.attend
                form.teamnumber.data = openData.teamnumber
                form.teamsize.data = openData.teamsize
                form.teamcount.data = openData.teamcount
                form.unit.data = openData.unit
                
            except: 
                pass 
    else:
        flash('Attendance not started', 'secondary') 
        return redirect(request.referrer)  

    return render_template('instructor/attInst.html', form=form, status=openData.teamnumber)     


def upload_picture(form_picture):    
    _ , f_ext = os.path.splitext(form_picture.filename) 
    s3_folder = 'profiles/'
    picture_filename =  current_user.username + f_ext 
    s3_filename =  s3_folder + current_user.username + f_ext     
    i1 = Image.open (form_picture) 
    i2 = i1.resize((100, 125), Image.NEAREST)
    i2.save (picture_filename)  
    i3 = Image.open (picture_filename) 
    with open(picture_filename, "rb") as image:
        f = image.read()
        b = bytearray(f)  

    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=s3_filename, Body=b)     
    return s3_filename    


@app.route("/account", methods=['GET','POST'])
@login_required 
def account():
    form = UpdateAccountForm() 
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = upload_picture(form.picture.data) 
            current_user.image_file = picture_file                   
        current_user.email = form.email.data        
        db.session.commit() 
        flash('Your account has been updated', 'success')
        return redirect (url_for('account')) 
    elif request.method == 'GET':       
        form.email.data = current_user.email
    # https://www.youtube.com/watch?v=803Ei2Sq-Zs&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=7    
    image_file = S3_LOCATION + current_user.image_file   
    
    return render_template('admin/account.html', title='Account', image_file = image_file, form=form ) 




