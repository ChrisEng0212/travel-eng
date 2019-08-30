import sys, boto3, random, base64, os, secrets, httplib2
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
    from aws import S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
except:
    pass

ColorScheme = ColorScheme.query.first()
S3_LOCATION = ColorScheme.Extra1
titleColor = ColorScheme.color1
bodyColor = ColorScheme.color2
headTitle = ColorScheme.Title1


@app.context_processor
def inject_user():
    return dict(titleColor=titleColor, bodyColor=bodyColor, headTitle=headTitle)

@app.route("/admin", methods = ['GET', 'POST'])
@login_required
def admin():       
    return render_template('admin/admin.html')



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
        user = User.query.filter_by(studentID=form.studentID.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): #$2b$12$UU5byZ3P/UTtk79q8BP4wukHlTT3eI9KwlkPdpgj4lCgHVgmlj1he  '123'
            login_user (user, remember=form.remember.data)
            next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url
            flash (f'Login Successful. Welcome back {current_user.username}.', 'success') 
            return redirect (next_page) if next_page else redirect (url_for('home')) # in python this is called a ternary conditional "redirect to next page if it exists"
        else: 
            flash (f'Login Unsuccessful. Please check {form.studentID.data} and {form.password.data}.', 'danger')          
    return render_template('admin/login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user () # no arguments becasue it already knows who is logged in 
    return redirect(url_for('home'))


@app.route ("/teams")
def teams():  
    if current_user.id != 1:
        return redirect(url_for('home')) 

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
   


def upload_picture(form_picture):
    #random_hex = secrets.token_hex(8)
    #rand = str(random.randint(1000,10000)) --- need to allow model to have more than 20 characters
    _ , f_ext = os.path.splitext(form_picture.filename) # _  replaces f_name which we don't need #f_ext  file extension 
    s3_folder = 'profiles/'
    picture_filename =  current_user.username + f_ext 
    s3_filename =  s3_folder + current_user.username + f_ext 
    temp_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    output_size = (125, 125)
    i = Image.open (form_picture)    
    i.thumbnail(output_size)   
    i.save(temp_path)
    data = open(temp_path, 'rb')        
    s3_resource = boto3.resource('s3',
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=s3_filename, Body=data)     
    return s3_filename    

    #s3_resource = boto3.resource('s3')
    #my_bucket = s3_resource.Bucket(S3_BUCKET)
    #my_bucket.Object(file_name).put(Body=file)


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




