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
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME   
except:
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']    


@app.route ("/", methods = ['GET', 'POST'])
@app.route ("/home", methods = ['GET', 'POST'])
@login_required
def home(): 
    if current_user.is_authenticated:
        attLog = AttendLog.query.filter_by(username=current_user.username).all()
    else:
        attLog = None
    
    attDict = {}
    for log in attLog:
        attDict[log]=[log.date_posted + timedelta(hours=8), log.attend, log.attScore, log.extraStr]


    return render_template('instructor/home.html', title='home', attLog=attLog, attDict=attDict)


@app.route ("/packing", methods = ['GET', 'POST'])
@login_required
def packing(): 
    
    noListOne = ['A: No, I need a new passport because....', 
            'B: No, I need to prepare the money, I will ....', 
            'C: No, actually I should book some tickets soon because....' 
    ]

    yesListOne = ['A: Yes, my passport is ready', 
            'B: Yes, I already prepared my money', 
            'C: Yes, I booked the tickets last _______' 
    ]
    
    noOne = random.choice(noListOne)      
    yesOne = []
    for item in yesListOne:
        if yesListOne.index(item) == noListOne.index(noOne):
            pass
        else:
            yesOne.append(item)

    #/////////////////////////

    noListTwo = ['A: No, I haven\'t got a powerbank because....', 
            'B: No, I won\'t bring a camera, I will ....', 
            'C: No, I need to get some earphones because....', 
            'D: No, I don\'t use an e-reader because....', 
            'E: No, I don\'t use a speaker, I can just....'
    ]

    yesListTwo = ['A: Yes, I need a powerbank for my ______', 
            'B: Yes, I need a camera to ______', 
            'C: Yes, I use earphones when I ________', 
            'D: Yes, my e-reader is good for ________', 
            'E: Yes, a speaker is useful when I _______'
    ]
    
    noTwo = random.choice(noListTwo)       
    yesTwo = []
    for item in yesListTwo:
        if yesListTwo.index(item) == noListTwo.index(noTwo):
            pass
        else:
            yesTwo.append(item)
    
    #/////////////////////////
    
    noListThr = ['A: No, I should get a swimsuit because....', 
            'B: No, I should get some walking shoes because ....', 
            'C: No, I need to get some new sunglasses so ....', 
            'D: No, a neck pillow is a good idea so ....', 
            'E: No, I might get a money belt because ....', 
            'F: No, I need a new hat because ....', 
            'G: No, but bug spray might help if ....', 
            'H: No, I might need a jacket if ....', 
            'I: No, I should get a new daypack because ....'

    ]

    yesListThr = ['A: Yes, my swimsuit is _____', 
            'B: Yes, my shoes are ______', 
            'C: Yes, my sunglasses are _______', 
            'D: Yes, my neckpillow is ________', 
            'E: Yes, I have a ________ money belt', 
            'F: Yes, I have a ________ travel hat', 
            'G: Yes, I have some ________ bug spray', 
            'H: Yes, I have a ________ travel jacket', 
            'I: Yes, my daypack is _________'
    ]
    
    noThr = random.choice(noListThr)   
    
    yesThr = []
    for item in yesListThr:
        if yesListThr.index(item) == noListThr.index(noThr):
            pass
        else:
            yesThr.append(item)
  
    context = {
        'noOne' : noOne, 
        'yesOne' : yesOne, 
        'noTwo' : noTwo, 
        'yesTwo' : yesTwo, 
        'noThr' : noThr, 
        'yesThr' : yesThr, 
    }


    return render_template('instructor/packing.html', title='Packing', **context)


@app.route("/nameSet", methods = ['POST'])
def nameSet(workname, custname):
    #custname = request.form['custname']

    modelItem = AgentList.query.filter_by(username=current_user.username).first()
    modelItem.extraStr = custname
    db.session.commit()
    print('commit')
    flash('Checking for match', 'secondary') 
    return redirect(url_for('agent_match', check=0))    

@app.route ("/agent_match/<int:check>", methods = ['GET', 'POST'])
@login_required
def agent_match(check):
     
    
    x = 0
    answers = AgentList.query.all() 
    for ans in answers:
        if current_user.username == ans.username:
            x += 1
    
    message = None
    
    if x < 3: 
        message = 'Keep going, you should try to meet 3 customers'
    elif x == 3:
        message = 'Maybe one more? Or close the Agency'
    elif x > 3:
        message = 'Maybe it is time to close the agency'
    else:
        message = None


    context = {
        'x' : x,
        'check' : check,
        'message' : message
    }          

    return render_template('instructor/agent_match.html', title='Agent', **context)

@app.route ("/agent_list", methods = ['GET', 'POST'])
@login_required
def agent_list():
    cust = Attendance.query.filter_by(role='cust').all()
    work = Attendance.query.filter_by(role='work').all() 
    custSet = AgentCust.query.all() 
    workSet = AgentWork.query.all()
    
    roleDict = {}   
    
    countW = 1
    for user in work:
        roleDict[countW] = [user.username, '-', '-', '-']
        countW +=1

    countC = 1
    for user in cust:
        if countC in roleDict:
            roleDict[countC][1] = user.username
        else:
            roleDict[countC] = ['-', user.username, '-', '-']
        countC +=1
    
    custNames = []
    for item in custSet:
        custNames.append(item.username)
    workNames = []
    for item in workSet:
        workNames.append(item.username)
    
    for key in roleDict:
        if roleDict[key][0] in workNames:
            roleDict[key][2] = roleDict[key][0]
        if roleDict[key][1] in custNames:
            roleDict[key][3] = roleDict[key][1]   

    print (roleDict)

    #create dictionary of answers
    ansDict = {}    
    custAns = AgentCust.query.all()    
    for ans in custAns:
        ansDict[ans.username] = [ans.A01, ans.A02, ans.A03, ans.A04, ans.A05, ans.A06]
    
    # create a list of names who duplicate
    names = []    
    ## create reverse dictionary to find duplicates
    revDict = {}
    for key in ansDict:
        values = str(ansDict[key])
        for item in revDict:
            if item == values:                   
                names.append(key)
                names.append(revDict[item])
        else: 
            revDict[values] = key
    
    print (ansDict)
    print (revDict)
    print (names)

    #calculate scores
    #     # {    
    #  agent : [matches, , ]}

    scores = []        
    matchesDict = {}
    answers = AgentList.query.all() 
    for ans in answers:
        matchesDict[ans.username] = []
        matchesList = eval(ans.match)
        if len(matchesList) > 1:
            for i in matchesList:
                matchesDict[ans.username].append('00' + i)
        elif len(matchesList) == 1:   
            matchesDict[ans.username].append(matchesList[0]) 
            scores.append(matchesList[0])
    
    print(scores)
    print(matchesDict)

    pairDict = {}
    scoreDict = {}
    for user in custSet:
        scoreDict[user.username] = 0 
        pairDict[user.username] = user.extraStr
        for i in scores:
            if i == user.username:
                scoreDict[user.username] +=1

    print(scoreDict)

    context = {
        'roleDict' : roleDict,
        'names' : names, 
        'scoreDict' : scoreDict,
        'matchesDict' : matchesDict  
    }          

    return render_template('instructor/agent_list.html', title='Agent', **context)


@app.route ("/agent", methods = ['GET', 'POST'])
@login_required
def agent(): 

    if Attendance.query.filter_by(username='Chris').first().role == 'closed':
        flash('Activity not started yet', 'danger') 
        return redirect(url_for('home'))

    attendCheck = Attendance.query.filter_by(username=current_user.username).first()
    if attendCheck:
        attend = attendCheck.role
    else:
        flash('Please attend the class first', 'danger') 
        return redirect(url_for('att_team'))
    
    if attend == 'cust':
        return redirect(url_for('agent_form', role='cust'))
    elif attend == 'work':
        return redirect(url_for('agent_form', role='work'))
    else:
        flash('Please attend the class first', 'danger') 
        return redirect(url_for('att_team'))        
    
    flash('No Data Available', 'danger') 
    return redirect(url_for('home'))
   


@app.route ("/agent_form/<string:role>", methods = ['GET', 'POST'])
@login_required
def agent_form(role):    
    
    if role == 'cust':
        form = AgentCustomer()
        model = AgentCust
        title = 'Conversation as Customer'        
    if role == 'work':
        form = AgentWorker()
        model = AgentWork
        title = 'Conversation as Travel Agent'
        
    work = Attendance.query.filter_by(role='work').all()     

    workNames = []
    for item in work:
        workNames.append(item.username)    

    #random pairer
    print(workNames)
    myList = []
    for i in range(7):
        x = random.choice(workNames)
        while x in myList:
            x = random.choice(workNames)
        myList.append(x)

    print(myList)    
    
    answers = model.query.filter_by(username=current_user.username).first()
    
    if answers:
        print ('action2')
        return redirect(url_for('agent_conv', role=role))    
    else:  
        if form.validate_on_submit():
            answers = model(username=current_user.username, 
            A01=form.A01.data,
            A02=form.A02.data,
            A03=form.A03.data,
            A04=form.A04.data,
            A05=form.A05.data,
            A06=form.A06.data, 
            extraStr = str(myList)
            )
            db.session.add(answers) 
            db.session.commit()
            flash('Ready for activity', 'success') 
            return redirect(url_for('agent_conv', role=role))
        else:
            pass

    context = {
        'form' : form, 
        'model' : model,
        'head' : title      
    } 

    return render_template('instructor/agent.html', title='Agent', **context)

@app.route ("/agent_conv/<string:role>", methods = ['GET', 'POST'])
@login_required
def agent_conv(role): 
    print ('action3')
    if role == 'cust':
        form = None        
        model = AgentCust
        title = 'Conversation as Customer'
        answers = model.query.filter_by(username=current_user.username).first()
        script = {
        1: 'Agent: Hi.... help?',
        2: AgentOne['1b'][0] + answers.A01,
        3: 'Agent: How long... ?',
        4: AgentOne['2b'][0] + answers.A02,
        5: 'Agent: Where.... ?',
        6: AgentOne['3b'][0] + answers.A03, 
        7: 'Agent: Have you considered...?',         
        8: AgentOne['4b'][0] + answers.A04, 
        9: 'Agent: What kind of accomodation....?', 
        10: AgentOne['5b'][0] + answers.A05, 
        11: 'Agent: (suggestion....)', 
        12: AgentOne['6b'][0] + answers.A06, 
        13: 'Agent: Okay....'
        }  

    if role == 'work':
        form = AgentListen()           
        model = AgentWork
        title = 'Conversation as Travel Agent'
        answers = model.query.filter_by(username=current_user.username).first()
        script = {
        1: 'CUSTOMER ARRIVES: ' + AgentOne['1a'][0] + answers.A01,
        2: 'Customer: I have vacation....', 
        3: AgentOne['2a'][0] + answers.A02,
        4: 'Customer: I have ___ days off',
        5: AgentOne['3a'][0] + answers.A03,
        6: 'Customer: I want to spend time in', 
        7: AgentOne['4a'][0] + answers.A04,         
        8: 'Customer: Okay...', 
        9: AgentOne['5a'][0] + answers.A05,  
        10: 'Customer: ', 
        11: AgentOne['xx'][0],        
        12: 'Customer: One more question', 
        13: AgentOne['6a'][0] + answers.A06        
        } 
        
        if form.validate_on_submit():
            if Attendance.query.filter_by(username='Chris').first().role == 'wait':
                flash('Waiting for all students to be ready', 'danger') 
                return redirect(url_for('agent_conv', role=role))
            else:
                pass

            #create dictionary of answers
            ansDict = {}
            custAns = AgentCust.query.all()
            # create a list of names who match
            names = []
            matches = []
            for ans in custAns:
                ansDict[ans.username] = [ans.A01, ans.A02, ans.A03, ans.A04, ans.A05, ans.A06]

            print (custAns)
            # find students with the same data set
            for key in ansDict:
                convAns = [form.C01.data, form.C02.data, form.C03.data, form.C04.data, form.C05.data, form.C06.data]
                print(convAns)
                if ansDict[key] == convAns:
                    names.append(key) 
                    myList = AgentCust.query.filter_by(username=key).first().extraStr
                    print (myList)                    
                    # if agents name in the list (eval(extraStr)) associated with that customer (key)                  
                    if current_user.username in eval(AgentCust.query.filter_by(username=key).first().extraStr):
                        matches.append(key)

            answers = AgentList(username=current_user.username, 
            C01=form.C01.data,
            C02=form.C02.data,
            C03=form.C03.data,
            C04=form.C04.data,
            C05=form.C05.data,
            C06=form.C06.data, 
            name=str(names), 
            match=str(matches)
            )
            db.session.add(answers) 
            db.session.commit() 

            if len(names) > 1:                
                if len(matches) == 1:
                    flash(('_______________________________ CONGRATUALTIONS: You have a possible match - Check with the instructor _______________________________'), 'info') 
                    check = 1 
            elif len(matches) == 1: 
                flash('_______________________________ CONGRATUALTIONS: You have a match with ' + str(matches) + ' _______________________________', 'success') 
                check = 0 
            else:
                flash(('_______________________________ SORRY: This conversation is not a match :( _______________________________'), 'danger') 
                check = 0 
            return redirect(url_for('agent_match', check=check))
        else:
            pass
    
    acco = [
        AgentOne['xx'][1][1],
        AgentOne['xx'][2][1],
        AgentOne['xx'][3][1],
        AgentOne['xx'][4][1]
        ]
    
    context = {
        'form' : form, 
        'script' : script,
        'head' : title, 
        'role' : role, 
        'acco' : acco     
    } 

    return render_template('instructor/agent_conv.html', title='Agent', **context)



######## Attendance //////////////////////////////////////////////
@app.route("/attend_team", methods = ['GET', 'POST'])
@login_required
def att_team():

    legend = 'Attendance: ' + time.strftime('%A %b, %d %Y %H:%M')

    # check if attendance is open 
    openData = Attendance.query.filter_by(username='Chris').first()
    if openData:
        openCheck = openData.teamnumber
        if openCheck == 98:  # open in normal state
            form = Attend()  
        elif openCheck == 99:  # switch to late form
            form = AttendLate() 
        elif openCheck == 100:   # delete all rows
            db.session.query(Attendance).delete()
            db.session.commit()
            attendance = Attendance(username = 'Chris', 
            attend='Notice', teamnumber=97, studentID='100000000')      
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance is not open yet, please try later', 'danger')
            return redirect(url_for('home')) 
        else: # openData has return None
            flash('Attendance is not open yet, please try later', 'danger')
            return redirect(url_for('home'))  
    else:
        flash('Attendance is not open yet, please try later', 'danger')
        return redirect(url_for('home'))  

    # set up page data 
    teamcount = openData.teamcount
    teamsize = openData.teamsize  
    notice = openData.attend     

    # set up student data   
    count = Attendance.query.filter_by(username=current_user.username).count()
    fields = Attendance.query.filter_by(username=current_user.username).first()     
    
    # set teamnumber to be zero by default (or not Zero in the case of solo classes)
    if teamsize == 0:
        teamNumSet = current_user.id + 100
    else:
        teamNumSet = 0 

    # set up team info 
    users = {}
    if count == 1: 
        teammates = Attendance.query.filter_by(teamnumber=fields.teamnumber).all()        
        for teammate in teammates:            
            image = User.query.filter_by(username=teammate.username).first().image_file
            users[teammate.username] = [teammate.username, S3_LOCATION + image]
    else:        
        users = None     

    # prepare initial form
    if count == 0:               
        if form.validate_on_submit():            
            # check last id for AttendLog 
            lastID = AttendLog.query.order_by(desc(AttendLog.id)).first().id   
            # team maker

            #role control
            wCount = Attendance.query.filter_by(role='work').count()
            if wCount > 20:
                flash('Sorry, there are too many TRAVEL AGENTS already. Please choose TRAVELLER', 'info')
                return redirect(url_for('att_team'))

            attendance = Attendance(username = form.name.data, 
            attend=form.attend.data, teamnumber=form.teamnumber.data, 
            teamcount=form.teamcount.data, studentID=form.studentID.data, unit=lastID+1, role=form.role.data)      
            db.session.add(attendance)
            db.session.commit()
            # long term log 
            if form.attend.data == 'On time':
                attScore = 3
            elif form.attend.data == 'Late': 
                attScore = 2
            else:
                attScore = 1          
            attendLog = AttendLog(username = form.name.data, 
            attend=form.attend.data,teamnumber=form.teamnumber.data, 
            studentID=form.studentID.data, attScore=attScore)
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
        # { 1 : 1,  2 : 1  ,  3 :  0 }
        teamDict = {}  
        for i in range (1,teamcount+1):
            count = Attendance.query.filter_by(teamnumber=i).count()
            if count: 
                teamDict[i] = count
            else:   
                teamDict[i] = 0
        print (teamDict)

        # all teams are full so make a new team
        if teamDict[teamcount] == teamsize:
            countField = Attendance.query.filter_by(username='Chris').first()
            countField.teamcount = teamcount +1            
            db.session.commit() 
            return redirect(url_for('att_team'))
        # all teams have the same number (first and last) of students so start from beginning
        elif teamDict[1] == teamDict[teamcount]:
            fields.teamnumber = 1
            db.session.commit()
            flash('Your attendance has been recorded', 'info')
            return redirect(url_for('att_team'))
        else:
            for key in teamDict:
                # search each group until one needs to be filled
                if teamDict[key] > teamDict[key+1]:
                    fields.teamnumber = key+1
                    db.session.commit()
                    flash('Your attendance has been recorded', 'info')
                    return redirect(url_for('att_team'))                 
                else: 
                    pass
    
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


