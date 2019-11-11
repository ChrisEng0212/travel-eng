import sys, boto3, random, os, time, datetime
from datetime import timedelta
from sqlalchemy import asc, desc 
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import * 
from models import *

try:
    from aws import Settings    
    s3_resource = Settings.s3_resource 
    s3_client = Settings.s3_client 
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME   
except:
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']    


#####  midterm FUNCTIONS ////////////////////////
def controls():   
    try:
        controls = MidTerm.query.filter_by(teamMemOne='100000000').order_by(asc(MidTerm.id)).all()   
        ##SET CONTROL  ##
        ## If control = None  ==> don't show extra features ##
        control = controls[0].extraInt # set extraInt to 1 and open the exam prep
        exOneID=controls[0].id         
        exTwoID=controls[1].id     
    except: 
        control = None
        exOneID=0
        exTwoID=0
        print('Controls Unsuccessful')

    return [control, exOneID, exTwoID]

def mtDictMaker(idNum):    
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
        if idNum:
            for dictList in studentDict[idNum]:
                names.append(dictList[1])    
                images.append(dictList[2]) 
            studentDict.pop(idNum) 
        for item in studentDict:
            for i in studentDict[item]:                           
                stids.append(i[0])     
    
    print('NAMES: ', names, 'IMAGES: ', images)
    print ('stids= ', stids)  
    print ('studentDict= ', studentDict) 
    return [studentDict, stids, names, images]

def fieldsChecker():
    # query the midterms and return the fields which the students is working on
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
      
    
    elif link.find('drive') != -1:     
        if link.find('open') != -1:  
            driveLink = link.split("=")
            code = driveLink[1]
            print('IF')            
        else:
            print('ELSE')
            driveLink = link.split("/")
            code = max(driveLink, key=len)

        embedSource = 'https://drive.google.com/file/d/' + code + '/preview'    
    
    else: 
        embedSource = link

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

    if 'Exam' in MidTerm.query.filter_by(id=1).first().extraStr or current_user.id == 1:
        allowed = MidTerm.query.all()
        for mod in allowed:
            allowedID.append(mod.id)      
    print ('allowedID', allowedID)


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
    
    #print("Fields: ", fields)
    #print("User: ", user)
    
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
            
    #print('ANSF', ansFields)
    
    #start exam grading
    #if user.exam == None:
        #user.exam = 0 
        #db.session.commit()    
    
    if form.validate_on_submit():                
        response = MidAnswers(A01=form.A01.data, A02=form.A02.data, 
        A03=form.A03.data, A04=form.A04.data, username=current_user.username, 
        grade=1, examID=idMarker) # add the id marker     
        db.session.add(response)                
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
            MidGrades.query.filter_by(username=name).first().midterm = 1
            db.session.commit() 


    # form in update mode
    if form.validate_on_submit():   
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
                MidGrades.query.filter_by(username=name).first().extraInt = 2
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
    # grades saved in User table, but also in MidGrades 
    # need to reorganize grading system 
    # show students how many listenings they should do
    # or show their grade on the home page 
    user = User.query.filter_by(username=current_user.username).first()  
    
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
            print ('pass1', exam.id)
            pass
        elif exam.checkQue == 1:            
            examList.append(exam.id)
        else:
            print ('pass2', exam.id)
            pass
    
    print ('available', examList)   
    
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


