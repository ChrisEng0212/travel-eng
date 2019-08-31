import sys, boto3, random, base64, os, time, datetime
from sqlalchemy import asc, desc 
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import * 
from models import *
try:
    from aws import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    s3_resource = boto3.resource('s3',
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
except:
    s3_resource = boto3.resource('s3')

ColorScheme = ColorScheme.query.first()
S3_LOCATION = ColorScheme.Extra1
S3_BUCKET_NAME = ColorScheme.Extra2


@app.route ("/", methods = ['GET', 'POST'])
@app.route ("/home", methods = ['GET', 'POST'])
def home():         
    return render_template('instructor/home.html', title='home')
    
######## Attendance //////////////////////////////////////////////
@app.route("/attend_solo", methods = ['GET', 'POST'])
@login_required
def att_solo():
    form = Attend()        


    # set up page data
    notice = Attendance.query.filter_by(username='Chris').first().attend    
    count = Attendance.query.filter_by(username=current_user.username).count()
    fields = Attendance.query.filter_by(username=current_user.username).first() 
    legend = 'Attendance: ' + time.strftime('%A %B, %d %Y %H:%M')

    if count == 0:        
        if form.validate_on_submit():

            attendance = Attendance(username = form.name.data, 
            attend=form.attend.data, teamnumber=form.teamnumber.data, 
            teamcount=form.teamcount.data, studentID=form.studentID.data)      
            db.session.add(attendance)            
            # long term log
            attendLog = AttendLog(username = form.name.data, 
            attend=form.attend.data,teamnumber=form.teamnumber.data, 
            studentID=form.studentID.data, attScore=3)
            db.session.add(attendLog)
            # commit both
            db.session.commit()
            flash('Your attendance has been recorded', 'info')
            return redirect(url_for('att_solo'))
        else:
            form.name.data = current_user.username
            form.studentID.data = current_user.studentID
            form.teamcount.data = 0
            form.teamnumber.data = 0  
     

    return render_template('student/attSolo.html', legend=legend, count=count, fields=fields, 
   form=form, notice=notice) 


@app.route("/attend_team", methods = ['GET', 'POST'])
@login_required
def att_team():
    form = Attend()    
     
    # check if teamcount has been set
    try:
        ## cannot filter by id because even if table is clear first will not be id ==1 
        teamcount = Attendance.query.filter_by(username='Chris').first().teamcount
        teamsize = Attendance.query.filter_by(username='Chris').first().teamsize
        print ('teamcount: ', teamcount, 'teamsize: ', teamsize)  
    except:    
        flash('Attendance is not open yet, please try later', 'danger')
        return redirect(url_for('home'))    

    # set teamcount to 100 to clear the table
    if teamcount == 100:        
        db.session.query(Attendance).delete()
        db.session.commit()
        flash('Attendance is not open yet, please try later', 'danger')
        return redirect(url_for('home')) 
    
    # set teamnumber to be zero by default (or not for solo classes)
    if teamsize == 0:
        teamNumSet = current_user.id + 100
    else:
        teamNumSet = 0 

    # set up page data
    
    notice = Attendance.query.filter_by(username='Chris').first().attend    
    count = Attendance.query.filter_by(username=current_user.username).count()
    fields = Attendance.query.filter_by(username=current_user.username).first() 
    legend = 'Attendance: ' + time.strftime('%A %B, %d %Y %H:%M')

    users = {}
    if count == 1: 
        teammates = Attendance.query.filter_by(teamnumber=fields.teamnumber).all()        
        for teammate in teammates:            
            image = User.query.filter_by(username=teammate.username).first().image_file
            users[teammate.username] = [teammate.username, S3_LOCATION + image]
    else:        
        users = None   
    

    #instructor teamnumber will not be updated from zero    
    if current_user.id == 1:
        return render_template('student/attTeam.html', legend=legend, count=count, fields=fields, 
    teamcount=teamcount, form=form, users=users, notice=notice) 

    if count == 0:               
        if form.validate_on_submit():
            # team maker
            attendance = Attendance(username = form.name.data, 
            attend=form.attend.data, teamnumber=form.teamnumber.data, 
            teamcount=form.teamcount.data, studentID=form.studentID.data)      
            db.session.add(attendance)
            # long term log
            attendLog = AttendLog(username = form.name.data, 
            attend=form.attend.data,teamnumber=form.teamnumber.data, 
            studentID=form.studentID.data, attScore=3)
            db.session.add(attendLog)
            # commit both
            db.session.commit()
            return redirect(url_for('att_team'))
        else:
            form.name.data = current_user.username
            form.studentID.data = current_user.studentID
            form.teamcount.data = 0
            form.teamnumber.data = teamNumSet  
    
    #after attendance is complete teamnumber 0 is reassigned to a team  
    elif fields.teamnumber == 0:

        teamList = list(range(1,teamcount+1))   
        print(teamList) 
        ## [1,2,3,4,5,6.........]

        #list counter determines average team distribution
        listCounter = []
        for i in teamList:            
            count = Attendance.query.filter_by(teamnumber=i).count()
            listCounter.append(count)        
        listAve = sum(listCounter)/len(listCounter)
        moduloTest = listAve%1
        print(listCounter)
        print(listAve) 
        
        if listAve == teamsize:
            countField = Attendance.query.filter_by(username='Chris').first()
            countField.teamcount = teamcount +1
            db.session.commit()
            return redirect(url_for('att_team'))
        elif moduloTest == 0:
            listCounter.reverse()                        
            posCounter = teamcount            
            for i in listCounter:
                if i < listAve:
                    # ex [2,2,2,2,2]  no i is less than ave:2 --> so skip through from end to find gaps 
                    # ex [2,1,1,0] zero is less than average --> fill the gap                   
                    fields.teamnumber = posCounter
                    db.session.commit()
                    return redirect(url_for('att_team'))  
                elif posCounter == 1:
                    ## no gaps to fill --> new row 
                    fields.teamnumber = 1
                    db.session.commit()
                    return redirect(url_for('att_team')) 
                else:
                    posCounter = posCounter - 1        
        else:
            while True: 
                for i in teamList:             
                    if listCounter[i-1] > listCounter[i]:
                        try:
                            #[3,3,3,2,2] --> TN = 4
                            if listCounter[i] == listCounter[i+1]:
                                fields.teamnumber = i + 1
                                db.session.commit()
                            else: 
                            #[3,3,3,2,0]  --> TN = 5
                                fields.teamnumber = i + 2
                                db.session.commit()
                        except: 
                            #[3,3,3,3,2] --> TN = 5
                            fields.teamnumber = i + 1
                            db.session.commit()
                        return redirect(url_for('att_team'))
                        break
                    else:
                        pass    
    
    flash('Your attendance has been recorded', 'info')
    return render_template('student/attTeam.html', legend=legend, count=count, fields=fields, 
    teamcount=teamcount, form=form, notice=notice, users=users) 
 


@app.route("/course", methods = ['GET', 'POST'])
@login_required
def course():
    sources = Sources.query.order_by(asc(Sources.date)).all()   
    return render_template('student/course.html', sources=sources)


#####  midterm FUNCTIONS ////////////////////////
def controls():   
    try:
        controls = MidTerm.query.filter_by(teamMemOne='100000000').order_by(asc(MidTerm.id)).all()   
        ##SET CONTROL  ##
        ## If control = None  ==> don't show extra features ##
        control = controls[0].extraInt   
        exOneID=controls[0].id         
        exTwoID=controls[1].id     
    except: 
        control = None
        exOneID=0
        exTwoID=0
        print('Controls Unsuccessful')

    return [control, exOneID, exTwoID]

def mtDictMaker(id):    
    model = MidTerm    
    mids = model.query.all()
    
    stids = []
    names = []
    images =[]    
    studentDict = {}    
    
    if mids:        
        for mid in mids:
            one = User.query.filter_by(studentID=mid.teamMemOne).first()
            two = User.query.filter_by(studentID=mid.teamMemTwo).first()
            thr = User.query.filter_by(studentID=mid.teamMemThr).first()
            a = [mid.teamMemOne, one.username, S3_LOCATION + one.image_file] 
            b = [mid.teamMemTwo, two.username, S3_LOCATION + two.image_file]
            if thr:                 
                c = [mid.teamMemThr, thr.username, S3_LOCATION + thr.image_file]
                studentDict[mid.id] = [a,b,c]
            else:            
                studentDict[mid.id] = [a,b] 
        if id:
            for dictList in studentDict[id]:
                names.append(dictList[1])    
                images.append(dictList[2]) 
            studentDict.pop(id) 
        for item in studentDict:
            for i in studentDict[item]:                           
                stids.append(i[0])     
    
    print('NAMES: ', names, 'IMAGES: ', images)
    print ('stids= ', stids)  
    print ('studentDict= ', studentDict) 
    return [studentDict, stids, names, images]

def fieldsChecker():
    model = MidTerm
    fieldsCheck1 = model.query.filter_by(teamMemOne=current_user.studentID).first()
    fieldsCheck2 = model.query.filter_by(teamMemTwo=current_user.studentID).first()
    fieldsCheck3 = model.query.filter_by(teamMemThr=current_user.studentID).first() 

    if fieldsCheck1:
        fields = fieldsCheck1
    elif fieldsCheck2:
        fields = fieldsCheck2
    elif fieldsCheck3:
        fields = fieldsCheck3
    else:
        fields = None

    return fields

def embedMaker(link):
    # embedMaker handles various kinds of links uploaded from drive or youtube
    # link.find(x) = -1 means no index found
    if link.find('you') != -1:        
        youLink = link.split("/")
        preCode = youLink[len(youLink)-1]
        if preCode.find("watch") != -1:
            watchSplit = ((preCode.split("="))[1]).split("&")
            code = watchSplit[0]
        else:
            code = preCode
        embedSource = 'https://www.youtube.com/embed/' + code
        
    
    if link.find('drive') != -1:     
        if link.find('open') != -1:  
            driveLink = link.split("=")
            code = driveLink[1]
            print('IF')            
        else:
            print('ELSE')
            driveLink = link.split("/")
            code = max(driveLink, key=len)

        embedSource = 'https://drive.google.com/file/d/' + code + '/preview'    

    print('EMBED:', embedSource)      
    #  https://drive.google.com/file/d/13qoP_5wPYHguCUB8qNXCGUtI136rHfCB/view?usp=sharing    
    #  https://drive.google.com/open?id=13qoP_5wPYHguCUB8qNXCGUtI136rHfCB
    #  https://drive.google.com/file/d/1pdvh_mEnkXPKA3jivYIpYKTaoukxH5p3Yg/preview

    #  https://www.youtube.com/watch?v=gV7z7U_3uZc&feature=youtu.be
    #  https://www.youtube.com/embed/gV7z7U_3uZc?list=PLur_sUvPELY70T8NveIVMqQWCKESfiP6u
    #  https://youtu.be/gd-UV92rNPw
    #  https://www.youtube.com/embed/gV7z7U_3uZc 
    
    return embedSource


#####  midterm PAGES ////////////////////////


@app.route("/MTexample/<int:idMarker>", methods = ['GET', 'POST']) 
@login_required
def MTexample(idMarker): 
    
    if fieldsChecker():
        Uid = fieldsChecker().id
    else:
        Uid = None

    # only allow user and examples to be accessed  
    ex1 = controls()[1]
    ex2 = controls()[2]
    allowedID = [ex1, ex2, Uid]

    # open the exam 
    #allowed = MidTerm.query.all()
    #for mod in allowed:
        #allowedID.append(mod.id)      
    
    if idMarker not in allowedID:
        flash('THIS EXAM IS NOT AVAILABLE AT THE MOMENT', 'primary')
        return redirect(url_for('mid_term'))
    
    

    form = MidtermExample()
    formList = [
        form.A01, 
        form.A02, 
        form.A03, 
        form.A04
    ]
  
    
    # models    
    fields = MidTerm.query.filter_by(id=idMarker).first()
    user = User.query.filter_by(username=current_user.username).first()
    print("FFFF", fields)
    print("UUUU", user)
    
    # embedMaker
    link = fields.vidLink
    embedSource = embedMaker(link)

    # details
    mDM = mtDictMaker(idMarker)    
    names = mDM[2]
    images = mDM[3]  
    

    ansFields= [fields.qOne, fields.qTwo, fields.qThr, fields.qFor]
    
    ansCheck = MidAnswers.query.filter_by(username=current_user.username).all()
    # check if form has been done before    
    for ans in ansCheck:
        if ans.examID == idMarker:
            ansFields = ansFields + [ans.A01, ans.A02, ans.A03, ans.A04, fields.aOne, fields.aTwo, fields.aThr, fields.aFor]
            
    print('ANSF', ansFields)
    

    #start exam grading
    if user.exam == None:
        user.exam = 0 
        db.session.commit()    
    

    if form.validate_on_submit():        
        response = MidAnswers(A01=form.A01.data, A02=form.A02.data, 
        A03=form.A03.data, A04=form.A04.data, username=current_user.username, 
        grade=1, examID=idMarker) # add the id marker     
        db.session.add(response)                
        db.session.commit()

        user.exam = user.exam + 1 
        db.session.commit()   

        flash('Your answer has been submitted', 'success') 
        return redirect(request.url)
    
    

    return render_template('student/midterm_example.html', names=names, images=images, 
    fields=fields, form=form, formList=formList, embedSource=embedSource, ansFields=ansFields)


@app.route("/midterm_update", methods = ['GET' , 'POST'])
@login_required
def MTedit():
    form = MidtermSetUp()
    formList = [
        form.MT01,
        form.MT02,
        form.MT03,
        form.MT04,
        form.MT05        
    ]

    fields = fieldsChecker()
    model = MidTerm

    
    if fields == None: 
        if form.validate_on_submit():  
            mDM = mtDictMaker(None)                
            stids = mDM[1]
            duplicate = []
            if form.MT04.data in stids:
                duplicate.append(form.MT04.data)
            if form.MT05.data in stids: 
                duplicate.append(form.MT05.data)              
            response = model(teamNum=form.MT01.data, vidOption=form.MT02.data, 
            teamMemOne=form.MT03.data, teamMemTwo=form.MT04.data, teamMemThr=form.MT05.data, duplicate=duplicate, checkQue=0)
            db.session.add(response)
            db.session.commit() 
            flash('Your project has been set up', 'success') 
            return redirect(url_for('MTbuild'))            
        elif request.method == 'GET':
            form.MT03.data = current_user.studentID
            return render_template('student/midterm_start.html', formList=formList, form=form, fields=None)   
        else:
            print('FORM ERROR', form.errors)

    mDM = mtDictMaker(fields.id)                
    stids = mDM[1]
    names = mDM[2]
    images = mDM[3]  
    
   
    if form.validate_on_submit():        
        fields.teamNum = form.MT01.data
        fields.vidOption = form.MT02.data
        fields.teamMemOne = form.MT03.data
        fields.teamMemTwo = form.MT04.data
        fields.teamMemThr = form.MT05.data 
        fields.names = None

        mDM = mtDictMaker(fields.id)                
        stids = mDM[1]
        duplicate = []
        if form.MT04.data in stids:
            duplicate.append(form.MT04.data)
        if form.MT05.data in stids: 
            duplicate.append(form.MT05.data) 
        fields.duplicate = duplicate

        db.session.commit()
        flash('Your project has been set up', 'success') 
        return redirect(url_for('MTbuild'))  
    elif request.method == 'GET':
        if fields.teamNum == None:
            form.MT03.data = current_user.studentID
        else:        
            form.MT01.data = fields.teamNum
            form.MT02.data = fields.vidOption
            form.MT03.data = current_user.studentID
            form.MT04.data = fields.teamMemTwo 
            form.MT05.data = fields.teamMemThr

    return render_template('student/midterm_start.html', formList=formList, form=form, fields=fields)


@app.route("/midterm_build", methods = ['GET', 'POST'])
@login_required
def MTbuild():        

    model = MidTerm
    
    fields = fieldsChecker()
    
    if fields == None:
        return redirect(url_for('MTedit'))

    form = MidtermDetails()
    formList = [        
        form.MT06, 
        form.MT07,
            form.MT08,        
            form.MT12,
        form.MT09,
        form.MT13,
            form.MT10,        
            form.MT14,
        form.MT11,
        form.MT15
    ]   
    
    fieldsList = [              
        fields.scrLink,
        fields.vidLink,
        fields.qOne,
        fields.aOne,
        fields.qTwo, 
        fields.aTwo,      
        fields.qThr,
        fields.aThr,
        fields.qFor,
        fields.aFor        
    ]    

    mDM = mtDictMaker(fields.id)                
    stids = mDM[1]
    names = mDM[2]
    images = mDM[3]   

    #add names
    if fields.names == None:        
        fields.names = names 
        db.session.commit() 
        for name in names:
            User.query.filter_by(username=name).first().midterm = 1
            db.session.commit() 

    # form in update mode
    if form.validate_on_submit():   
        fields.scrLink = form.MT06.data
        fields.vidLink = form.MT07.data
        fields.qOne = form.MT08.data
        fields.qTwo = form.MT09.data 
        fields.qThr = form.MT10.data
        fields.qFor = form.MT11.data 
        fields.aOne = form.MT12.data
        fields.aTwo = form.MT13.data 
        fields.aThr = form.MT14.data
        fields.aFor = form.MT15.data
        
        count = 0
        for i in formList:
            if i.data == "":
                count = count + 1 
        if count > 0:
            fields.checkQue = 0
        else:
            if fields.checkQue > 0:
                pass
            else:
                fields.checkQue = 1        
        db.session.commit()
        
        if fields.checkQue == 1:
            for name in names:
                User.query.filter_by(username=name).first().midterm = 2
                db.session.commit() 

        flash('Your project has been updated', 'success') 
        return redirect(request.url)  
    elif request.method == 'GET':
        for k in range(0,10):
            formList[k].data = fieldsList[k]    
    else:
        print(form.errors)  

    return render_template('student/midterm_build.html', formList=formList, form=form, fields=fields, names=names, images=images)


@app.route("/midterm", methods = ['GET', 'POST'])
@login_required
def mid_term():
    user = User.query.filter_by(username=current_user.username).first()
    userMidterm = user.midterm
    userExam = user.exam

    midExams = MidTerm.query.all()
    modAnswers = MidAnswers.query.filter_by(username=current_user.username).all()

    control = controls()[0]
    exOneID = controls()[1]
    exTwoID = controls()[2]  
    exTestOne=0
    exTestTwo=0
    testProj=0

        
    #find id of user's project (if they have one)   
    if fieldsChecker() == None:        
        userID = 0
    else:
        userID = fieldsChecker().id
    #is id in the MidAnswers = projTest completed 

    #make list of completed exams
    idList = []   
    for mod in modAnswers:  
        ansID = mod.examID
        #project is finished and it's been tested   
        if ansID == userID:            
            testProj = 1         
        if ansID == exOneID:
            exTestOne = 1                     
        if ansID == exTwoID:
            exTestTwo = 1 
        idList.append(ansID)

    print('ID_LIST', idList)

    examList = []   
    #generate random exam 
    for exam in midExams:
        if exam.id in idList:
            pass
        else:
            examList.append(exam.id)
    try:
        randID = random.choice(examList)
    except:
        randID = 0
    
    
    context = {
        'user' : user, 
        'userID': userID,
        'randID' : randID,         
        'idList' : idList, 
        'examList' : examList,
        'testProj' : testProj,   
        'exOneID' : exOneID, 
        'exTestOne' : exTestOne,     
        'exTwoID' : exTwoID, 
        'exTestTwo' : exTestTwo,  
        'control' : control 
    }

    return render_template('student/midterm.html', **context)


######## Units //////////////////////////////////////////////

@app.route ("/final")
def final():
    #this will redirect to the root url    
    return render_template('student/final.html' )

def team_details ():
    # check user has a team number
    try:
        teamnumber = Attendance.query.filter_by(username=current_user.username).first().teamnumber
        if teamnumber == 0:
            namesRange = current_user.username 
        else:
        # confirm names of team
            names = Attendance.query.filter_by(teamnumber=teamnumber).all()   
            nameRange = []
        for student in names:
            nameRange.append(student.username)    
        print ('NAMES', nameRange)
    except: 
        # create a unique teamnumber for solo users
        teamnumber = current_user.id + 100
        nameRange = current_user.username 
        print ('Teamnumber: ', teamnumber)
    return [teamnumber, nameRange]

def create_folder(unit, teamnumber, nameRange):
    #s3_resource = boto3.resource('s3',
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    s3_client = boto3.client('s3',
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    keyName = (unit + '/' + teamnumber + '/')  #adding '/' makes a folder object

    try: 
        # use s3_client instead of resource to use head_object or list_objects
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=keyName)
        print('Folder Located')   
    except:
        s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=keyName) 
        object = s3_resource.Object(S3_BUCKET_NAME, keyName + str(nameRange) + '.txt')         
        object.put(Body='some_binary_data') 
        print('Folder Created')          
    else:
        pass    
    return keyName
    

def unit_audio(audio, unit, team, rec):    
    _ , f_ext = os.path.splitext(audio.filename) # _  replaces f_name which we don't need #f_ext  file extension 
    s3_folder = '/unit_audio/'
    audio_filename =  s3_folder + unit + 'Team' + team + '_' + rec + f_ext 
    s3_filename =  S3_LOCATION + audio_filename 
    #s3_resource = boto3.resource('s3',
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key= AWS_SECRET_ACCESS_KEY)  
    #s3_resource = boto3.resource('s3')
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=audio_filename, Body=audio) 
      
    return s3_filename  

@app.route ("/unit/<string:unit_num>", methods=['GET','POST'])
@login_required
def unit(unit_num):
        
    teamdeets = team_details ()
    teamnumber = teamdeets[0]
    nameRange = teamdeets[1]   
     
    # models update
    modList = Info.modListUnits    

    #set form  / model / source
    form = Project()    
    model = modList[int(unit_num)]          
    source = Sources.query.filter_by(unit=unit_num).first()

    keyName = create_folder(unit_num, str(teamnumber), nameRange)


   #check source to see if unit is open yet
    if source.openSet == 1:    
        pass
    else:
        flash('This unit is not open at the moment', 'danger')
        return redirect(url_for('unit_list'))    
        
    #start unit assignment
    fieldsCheck = model.query.filter_by(teamnumber=teamnumber).first()  
    if fieldsCheck == None:
        response = model(teamNames=nameRange, teamnumber=teamnumber, topic=source.topic)
        db.session.add(response)
        db.session.commit()        
        return redirect(request.url)
    else: 
        fields = model.query.filter_by(teamnumber=teamnumber).first() 

    
    listList = [] 
    numList = ["One", "Two", "Three", "Four", "Five", "Six"]
    for i in numList:
        tex = "Text" + i
        pic = "Picture" + i 
        rec = "Record" + i 
        listList.append(tex)
        listList.append(pic)
        listList.append(rec)    
    
    print(listList)
    modelList = []  
    formList = [] 
    fieldsList = []
    for j in listList:        
        formList.append(getattr(form, j)) 
        fieldsList.append(getattr(fields, j))
        modelList.append(getattr(model, j))

    print(fieldsList)

    fieldsList2 = [
        fields.TextOne,
        fields.PictureOne, 
        fields.RecordOne,
        fields.TextTwo,
        fields.PictureTwo, 
        fields.RecordTwo,
        fields.TextThree,
        fields.PictureThree, 
        fields.RecordThree,
        fields.TextFour,
        fields.PictureFour, 
        fields.RecordFour,
        fields.TextFive,
        fields.PictureFive, 
        fields.RecordFive,
        fields.TextSix,
        fields.PictureSix, 
        fields.RecordSix     
    ]

    formList2 = [
        form.TextOne,
        form.PictureOne, 
        form.RecordOne,
        form.TextTwo,
        form.PictureTwo, 
        form.RecordTwo,
        form.TextThree,
        form.PictureThree, 
        form.RecordThree,
        form.TextFour,
        form.PictureFour, 
        form.RecordFour,
        form.TextFive,
        form.PictureFive, 
        form.RecordFive,
        form.TextSix,
        form.PictureSix, 
        form.RecordSix     
    ]
    
    print(fields.Complete)
    #deal with the form
    if form.validate_on_submit():    
        fields.TextOne = form.TextOne.data
        fields.PictureOne = form.PictureOne.data 
        fields.RecordOne = form.RecordOne.data
        fields.TextTwo = form.TextTwo.data
        fields.PictureTwo = form.PictureTwo.data 
        fields.RecordTwo = form.RecordTwo.data
        fields.TextThree = form.TextThree.data
        fields.PictureThree = form.PictureThree.data 
        fields.RecordThree = form.RecordThree.data
        fields.TextFour = form.TextFour.data
        fields.PictureFour = form.PictureFour.data 
        fields.RecordFour = form.RecordFour.data
        fields.TextFive = form.TextFive.data
        fields.PictureFive = form.PictureFive.data 
        fields.RecordFive = form.RecordFive.data
        fields.TextSix = form.TextSix.data
        fields.PictureSix = form.PictureSix.data 
        fields.RecordSix = form.RecordSix.data  
                  
        if fields.Complete == None:            
            fields.Complete = 1    
        db.session.commit()
        flash('Your answer has been recorded', 'success') 
        return redirect(request.url)
    elif request.method == 'GET': 
        print('no luck buddy')  
        for k in range(0,18):
            formList[k].data = fieldsList[k]
    else:
        print(form.errors)
    
    context = {
        'form' : form, 
        'fields' : fields, 
        'fieldsList' : fieldsList, 
        'formList' : formList,   
        'topic' : model.topic, 
        'team' : model.teamNames        
    }

    return render_template('student/project_layout.html', **context)


