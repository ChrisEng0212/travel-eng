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


    return render_template('activity/packing.html', title='Packing', **context)


@app.route("/nameSet", methods = ['POST'])
def nameSet(workname, custname):
    #custname = request.form['custname']

    modelItem = AgentList.query.filter_by(username=current_user.username).first()
    modelItem.extraStr = custname
    db.session.commit()
    print('commit')
    flash('Checking for match', 'secondary') 
    return redirect(url_for('agent_match', check=0))    


@app.route ("/agent_list", methods = ['GET', 'POST'])
@login_required
def agent_list():

    custCount = Attendance.query.filter_by(role='cust').count()
    workCount = Attendance.query.filter_by(role='work').count()
    cust = Attendance.query.filter_by(role='cust').all()
    work = Attendance.query.filter_by(role='work').all() 
    custSet = AgentCust.query.all() 
    workSet = AgentWork.query.all()
    
    roleDict = {} 
    if custCount > workCount:
        for i in range (custCount):
            roleDict[i+1] =  ['-', '-', '-', '-']
            count = custCount
    else:
        for i in range (workCount):
            roleDict[i+1] =  ['-', '-', '-', '-']
            count = workCount


    # list of roles
    for user in work:
        for i in range(count):
            if roleDict[i+1][0] != '-':
                pass
            else:             
                roleDict[i+1][0] = user.username
                break

    for user in cust:
        for i in range(count):
            if roleDict[i+1][1] != '-':
                pass
            else:             
                roleDict[i+1][1] = user.username
                break
    
    # list of set students
    for item in workSet:
        for key in roleDict:
            if roleDict[key][0] == item.username:
                roleDict[key][2] = item.username
                break
    for item in custSet:
        for key in roleDict:
            if roleDict[key][1] == item.username:
                roleDict[key][3] = item.username
                break

    # create a list of names who duplicate
    names = []  

    #create dictionary of answers
    ansDict = {} 
    for ans in custSet:
        ansDict[ans.username] = str([ans.A01, ans.A02, ans.A03, ans.A04, ans.A05, ans.A06])
    
    #compare values in the dictionary
    for key in ansDict:
        for check in ansDict:
            if ansDict[key] == ansDict[check]:
                if key != check:
                    if (check + key) in names:
                        pass
                    else:                        
                        names.append(key + check)
         
      
    # create reverse dictionary to find duplicates
    #revDict = {}
    #for key in ansDict:
    #    values = str(ansDict[key])
    #    for item in revDict:
    #        if item == values:                   
    #            names.append(key)
    #            names.append(revDict[item])
    #    else: 
    #        revDict[values] = key
    
    print (ansDict)    
    print (names)

    performDict = {}
    attend = Attendance.query.all()
    answers = AgentList.query.all() 
    for user in attend:
        performDict[user.username] = None
    
    for user in performDict: 
        matches = []
        for ans in answers:
            if ans.username == user: 
                if ans.match != '[]':              
                    matches.append(ans.match)        
        performDict[user] = matches
                
   
    for user in performDict: 
        if performDict[user] == None:
            pass
        else: 
            break            
        nameList = []  
        matchList = []      
        for ans in answers:
            nameEval = eval(str(ans.name))
            if  nameEval == user: 
                names.append(nameEval)
            matchEval = eval(str(ans.match))
            if  matchEval == user: 
                names.append(matchEval)  

        print('xxx', nameList, matchList)
        performDict[user] = str(len(matchList)) + '/' + str(len(nameList))


    scores = []        
    matchesDict = {}
    # username : [     ]
    answers = AgentList.query.all() 
    for ans in answers:
        matchesDict[ans.username] = []        
        matchesList = eval(ans.match)
        if len(matchesList) > 1:
            for i in matchesList:
                matchesDict[ans.username].append('00' + i)
        elif len(matchesList) == 1: 
            # name of TA : [cust, cust]  
            matchesDict[ans.username].append(matchesList[0]) 
            # for counting the grade
            scores.append(matchesList[0])
    
    print(scores)
    print(matchesDict)

    pairDict = {}
    scoreDict = {}
    for user in custSet:
        #set score to zero
        scoreDict[user.username] = 0 
        #set list of TAs
        pairDict[user.username] = user.extraStr
        for i in scores:
            if i == user.username:
                scoreDict[user.username] +=1

    print(scoreDict)

    context = {
        'roleDict' : roleDict,
        'names' : names, 
        'scoreDict' : scoreDict,
        'matchesDict' : matchesDict, 
        'performDict' : performDict
    }          

    return render_template('activity/agent_list.html', title='Agent', **context)

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

    return render_template('activity/agent.html', title='Agent', **context)

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
                    flash(('_______________________________ CONGRATUALTIONS: You have a possible match - Check with the activity _______________________________'), 'info') 
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

    return render_template('activity/agent_conv.html', title='Agent', **context)


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

    return render_template('activity/agent_match.html', title='Agent', **context)


### IMMIGRATION ##################################


@app.route ("/immig_list", methods = ['GET', 'POST'])
@login_required
def immig_list():

    custCount = Attendance.query.filter_by(role='cust').count()
    workCount = Attendance.query.filter_by(role='work').count()
    cust = Attendance.query.filter_by(role='cust').all()
    work = Attendance.query.filter_by(role='work').all() 
    custSet = ImmigTrav.query.all() 
    workSet = ImmigOffr.query.all()
    
    
    workDict = {} 
    for item in work:
        workDict[item.username] = [1, 0, []]
    for item in workSet:
        if workDict[item.username]:
            workDict[item.username][0] = 'Set'
    print('workDict', workDict)  

    custDict = {}
    for item in cust:
        custDict[item.username] = [1, 0, []]
    for item in custSet:
        if custDict[item.username]:
            custDict[item.username][0] = 'Set'
    
    print('custDict', custDict) 

    
    # create a list of names who duplicate
    names = []  
    #create dictionary of answers
    ansDict = {} 
    for ans in custSet:
        ansDict[ans.username] = str([ans.A01, ans.A02, ans.A03, ans.A04, ans.A05, ans.A06])    
    #compare values in the dictionary
    for key in ansDict:
        for check in ansDict:
            if ansDict[key] == ansDict[check]:
                if key != check:
                    if (check + key) in names:
                        pass
                    else:                        
                        names.append(key + check)
      
    print ('ansDict', ansDict)    
    print (' names', names)       
   
    answers = ImmigList.query.all() 
    for ans in answers:
        if workDict[ans.username]:
            workDict[ans.username][1] += 1
            workDict[ans.username][2].append(ans.match)
    for ans in answers:
        if ans.name in custDict:
            custDict[ans.name][2].append(ans.username)
       
    context = {
        'workDict' : workDict,
        'custDict' : custDict, 
        'names' : names
    }          

    return render_template('activity/immig_list.html', title='Immigration', **context)


@app.route ("/immig", methods = ['GET', 'POST'])
@login_required
def immig(): 

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
        return redirect(url_for('immig_form', role='cust'))
    elif attend == 'work':
        return redirect(url_for('immig_form', role='work'))
    else:
        flash('Please attend the class first', 'danger') 
        return redirect(url_for('att_team'))        
    
    flash('No Data Available', 'danger') 
    return redirect(url_for('home'))
   


@app.route ("/immig_form/<string:role>", methods = ['GET', 'POST'])
@login_required
def immig_form(role):    
    
    if role == 'cust':
        form = ImmigTraveller()
        model = ImmigTrav
        title = 'Conversation as Traveller'        
    if role == 'work':
        form = ImmigOfficer()
        model = ImmigOffr
        title = 'Conversation as Immigration Officer'
        
    work = Attendance.query.filter_by(role='work').all()     

    workNames = []
    for item in work:
        workNames.append(item.username)    

    #random pairer
    print(workNames)
    myList = []
    if len(workNames) > 5:    
        for i in range(6):
            x = random.choice(workNames)
            while x in myList:
                x = random.choice(workNames)
            myList.append(x)
    else: 
        myList = workNames

    print(myList)    
    
    answers = model.query.filter_by(username=current_user.username).first()
    
    if answers:
        print ('action2')
        return redirect(url_for('immig_conv', role=role))    
    else:  
        if form.validate_on_submit():
            answers = model(username=current_user.username, 
            A01=form.A01.data,
            A01x=form.A01x.data,
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
            return redirect(url_for('immig_conv', role=role))
        else:
            pass

    context = {
        'form' : form, 
        'model' : model,
        'head' : title      
    } 

    return render_template('activity/immig.html', title='Immigration', **context)

@app.route ("/immig_conv/<string:role>", methods = ['GET', 'POST'])
@login_required
def immig_conv(role): 
    print ('action3')
    if role == 'cust':
        form = None        
        model = ImmigTrav
        title = 'Conversation as Traveller'
        image = 'https://travel-eng.s3-ap-northeast-1.amazonaws.com/images/immig_traveller.PNG'
        answers = model.query.filter_by(username=current_user.username).first()
        script = {
        1: 'Officer: Coming from?',
        2: ImmigOne['1b'][0] + answers.A01,
        ####        
        3: 'Officer: PASSPORT',
        4: ImmigOne['1d'][0] + answers.A01x,
        ####
        5: 'Officer: PURPOSE?',
        6: ImmigOne['2b'][0] + answers.A02,
        7: 'Officer: JOB?',
        8: ImmigOne['3b'][0] + answers.A03, 
        9: 'Officer: ACCOMODATION?',         
        10: ImmigOne['4b'][0] + answers.A04, 
        11: 'Officer: TIME?', 
        12: ImmigOne['5b'][0] + answers.A05, 
        13: 'Officer: VISIT BEFORE?', 
        14: ImmigOne['6b'][0] + answers.A06, 
        15: 'Officer: Allowed/Not Allowed'
        }  

    if role == 'work':
        form = ImmigListen()           
        model = ImmigOffr
        title = 'Conversation as Immigration Officer'
        image = 'https://travel-eng.s3-ap-northeast-1.amazonaws.com/images/immig_officer_clipped.jpg'
        answers = model.query.filter_by(username=current_user.username).first()
        script = {
        1: 'TRAVELLER ARRIVES: ' + ImmigOne['1a'][0] + answers.A01,
        2: 'Traveller: Coming from..', 
        3: ImmigOne['1c'][0] + answers.A01x,
        4: 'Traveller: CHECK PASSPORT',
        5: ImmigOne['2a'][0] + answers.A02,
        6: 'Traveller: REASON FOR TRAVEL', 
        7: answers.A03,         
        8: 'Traveller: JOB', 
        9: answers.A04,  
        10: 'Traveller: ACCOMODATION', 
        11: answers.A05,        
        12: 'Traveller: TIME', 
        13: answers.A06,
        14: 'Traveller: VISIT BEFORE',
        15: 'Let me check if you are approved or denied...'
        } 
        
        if form.validate_on_submit():
            if Attendance.query.filter_by(username='Chris').first().role == 'wait':
                flash('Waiting for all students to be ready', 'danger') 
                return redirect(url_for('immig_conv', role=role))
            else:
                pass

            #create dictionary of answers
            ansDict = {}
            custAns = ImmigTrav.query.all()
            # create a list of names who match
            name = 'None'
            match = None
            for ans in custAns:
                ansDict[ans.username] = [ans.A01, ans.A02, ans.A03, ans.A04, ans.A05, ans.A06]

            print (custAns)
            # find students with the same data set
            for key in ansDict:
                convAns = [form.C01.data, form.C02.data, form.C03.data, form.C04.data, form.C05.data, form.C06.data]
                print(convAns)
                if ansDict[key] == convAns:
                    name = key
                    myList = ImmigTrav.query.filter_by(username=key).first().extraStr
                    print (myList)                    
                    # if officers name in the list (eval(extraStr)) associated with that customer (key)                  
                    if current_user.username in eval(ImmigTrav.query.filter_by(username=key).first().extraStr):
                        match = key

            answers = ImmigList(username=current_user.username, 
            C01=form.C01.data,
            C02=form.C02.data,
            C03=form.C03.data,
            C04=form.C04.data,
            C05=form.C05.data,
            C06=form.C06.data, 
            name=str(name), 
            match=str(match)
            )
            db.session.add(answers) 
            db.session.commit() 

            
            if match == None: 
                result = 0                                
                flash(('SORRY: This conversation is not a match :('), 'danger') 
            else:
                result = 1
                flash('CONGRATUALTIONS: You have a match with ' + match , 'success') 
               
            return redirect(url_for('immig_match', result=result, name=name))
         
        
    context = {
        'form' : form, 
        'script' : script,
        'head' : title, 
        'role' : role,
        'image' : image
    }         

    return render_template('activity/immig_conv.html', title='Immigration', **context)


@app.route ("/immig_match/<int:result>/<string:name>", methods = ['GET', 'POST'])
@login_required
def immig_match(result, name):  
    
    
    context = {        
        'result' : result,
        'name' : name
        
    }          

    return render_template('activity/immig_match.html', title='Immigration', **context)
