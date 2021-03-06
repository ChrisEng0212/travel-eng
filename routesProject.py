import sys, boto3, random, os
from sqlalchemy import asc, desc 
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import * 
from models import *
import ast # eval literal for list str

try:
    from aws import Settings    
    s3_resource = Settings.s3_resource 
    s3_client = Settings.s3_client 
    S3_LOCATION = Settings.S3_LOCATION
    S3_BUCKET_NAME = Settings.S3_BUCKET_NAME
    test = True   
except:
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    S3_LOCATION = os.environ['S3_LOCATION'] 
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']   
    test = False 

modList = [
        None,
        P1_NM, 
        P2_TA, 
        P3_TD,
        P4_HT
        ]

queryList = {
       1 : P1_NM.query.all(), 
       2 : P2_TA.query.all(), 
       3 : P3_TD.query.all(), 
       4 : P4_HT.query.all()

    }   

titles = [
        None, 
        'At the Night Market', 
        'Around Taipei', 
        'Taiwan Destinations', 
        'Survival Guide'
        ]


@app.route ("/final")
def final():  
      
    projDict = {
        1: ['0', titles[1], 'No Team Yet', '0', None, 0],
        2: ['0', titles[2], 'No Team Yet', '0', None, 0], 
        3: ['0', titles[3], 'No Team Yet', '0', None, 0],
        4: ['0', titles[4], 'No Team Yet', '0', None, 0]          
    } 

    # check each model
    for queryInt in queryList:
        stopCounter = 0 
        for row in queryList[queryInt]:                                   
            if current_user.username in ast.literal_eval(row.teamNames):
                #print (ast.literal_eval(row.teamNames))
                status = ast.literal_eval(row.Status)
                print (row.Status)
                projDict[queryInt] = [str(queryInt), titles[queryInt], ast.literal_eval(row.teamNames), str(row.teamNumber), status, sum(status)]               
    
    if test: 
        href = 'http://127.0.0.1:5000/project/'
        href2 = 'http://127.0.0.1:5000/projtest/'

    else: 
        href = 'https://travel-eng.herokuapp.com/project/'
        href2 = 'https://travel-eng.herokuapp.com/projtest/'
    

    print (projDict)

    testModels = [None, P1_EX, P2_EX, P3_EX, P4_EX]

    studentTest = {
        1: 0,
        2: 0, 
        3: 0,
        4: 0    
    } 

    examDict = {
        1 : { 
            'points' : 0, 
            'exams' : []        
        },
        2 : { 
            'points' : 0, 
            'exams' : []        
        }, 
        3 : { 
            'points' : 0, 
            'exams' : []        
        }, 
        4 : { 
            'points' : 0, 
            'exams' : []        
        }      
    }

    # 3 -4 to exam Dict and make range 1,5
    for i in range(1,5):
        completed = testModels[i].query.filter_by(studentName=current_user.username).all()
        print('Completed', completed)
        if completed: 
            for row in completed:   
                # find if it was a test or not             
                if row.projTeam == int(projDict[i][3]):
                    studentTest[i] = sum(ast.literal_eval(row.status))                
                else:   
                    if i > 5:
                        #so no pass to display all four projects
                        pass
                    else:                 
                        examDict[i]['exams'].append(row.projTeam)
                        if sum(ast.literal_eval(row.status)) == 5:
                            examDict[i]['points'] += 1



    print ('scores:', studentTest) 
    print ('exam: ', examDict)  

    return render_template('project/final.html', projDict=projDict, href=href, href2=href2, studentTest=studentTest, examDict=examDict)
 

def create_folder(unit, teamnumber, nameRange): 
    keyName = (unit + '/' + teamnumber + '/')  #adding '/' makes a folder object
    print (keyName)
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
        print('Pass')  
        pass

    return keyName


@app.route ("/proteams/<string:unit>/", methods=['GET','POST'])
@login_required
def project_teams(unit):
    if current_user.id != 1:
        return abort(403)

    modList = [
        None,
        P1_NM, 
        P2_TA, 
        P3_TD, 
        P4_HT
        ]

    project = modList[int(unit)]

    teams = []
    for pro in project.query.all():
        teams.append(pro.teamNumber)    

    #create a dictionary of teams
    attTeams = Attendance.query.all()
    teamsDict = {}
    for att in attTeams:
        if att.teamnumber in teamsDict:
            teamsDict[att.teamnumber].append(att.username)
        else: 
            teamsDict[att.teamnumber] = [att.username]    
    
    manualAdd = {
        20: ['Felisia', 'Angus', 'Victor', 'Winnie'],        
    }

    #add the extra teams -->  dictionary = teamsDict --> manualAdd
    dictionary = manualAdd

    returnStr = str(dictionary)
    for team in dictionary:
        if team in teams:
            returnStr = 'Error - check table' 
            break    
        create_folder(unit, str(team), dictionary[team])
        teamStart = project(
            teamNumber=team, 
            teamNames=str(dictionary[team]),
            Status=str([0,0,0,0,0])
            )        
        db.session.add(teamStart)
        db.session.commit()  

    return returnStr 


def upload_data(data, unit, team, mark):   
    # S3_Location / 1 / 1 / mark 
    _ , f_ext = os.path.splitext(data.filename) # _  replaces f_name which we don't need #f_ext  file extension     
    data_filename =  str(unit) + '/' + str(team) + '/' + mark + f_ext 
    s3_filename =  S3_LOCATION + data_filename     
    s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=data_filename, Body=data) 

    return data_filename

@app.route ("/project_dash", methods=['GET','POST'])
@login_required
def project_dash():
    
    users = User.query.all()

    studStats = {}

    for user in users:
        studStats[user.username] = [None, 0, 0, 0, 0]
    
    dashDict = {
        1 : {}, 
        2 : {}, 
        3 : {}, 
        4 : {}
    }
    
    count = 1
    for queryInt in queryList:
        for row in queryList[queryInt]: 
            status = ast.literal_eval(row.Status)
            names = ast.literal_eval(row.teamNames)
            dashDict[queryInt][count] = {
                'team' : str(row.teamNumber), 
                'names' : names, 
                'status' : status, 
                'score' : sum(status)  
            }
            for name in names:
                studStats[name][queryInt] = sum(status) 

            count += 1

    for user in users:
        if user.course != str(studStats[user.username]):        
            user.course = str(studStats[user.username])
            db.session.commit()


    # learn which students are missing    
    
    nameList = {
        1 : ['Tommy', 'Lulu', 'Test2', 'Rae', 'Sarah', 'Lin', 'Test', 'Jay', 'Alice'], 
        2 : ['Tommy', 'Lulu', 'Test2', 'Rae', 'Sarah', 'Lin', 'Test', 'Jay', 'Alice'], 
        3 : ['Tommy', 'Lulu', 'Test2', 'Rae', 'Sarah', 'Lin', 'Test', 'Jay', 'Alice'], 
        4 : ['Tommy', 'Lulu', 'Test2', 'Rae', 'Sarah', 'Lin', 'Test', 'Jay', 'Alice']
    }
    for key in dashDict:
        for entry in dashDict[key]:            
            for name in dashDict[key][entry]['names']:
                nameList[key].append(name)
     
    missList = {
        1 : [], 
        2 : [], 
        3 : [], 
        4 : []
    }

    for key in nameList:
        for user in users:
            if user.username not in nameList[key]:
                missList[key].append(user.username)

    print (missList[1])
    print (missList[2])
    print (missList[3])
    print (missList[4])
    return render_template('project/final_dash.html', dashDict=dashDict, missList=missList)
            
               
        


@app.route ("/project/<int:pro_num>/<int:team_num>/<int:part_num>", methods=['GET','POST'])
@login_required
def project_build(pro_num, team_num, part_num):
    
    
    proMod = modList[pro_num]   

    #search model for team
    teamModel = proMod.query.filter_by(teamNumber=team_num).first()
    names = ast.literal_eval(teamModel.teamNames)

    if current_user.id == 1:
        pass
    elif current_user.username not in names:
        flash('The exam has not started yet', 'danger')
        return redirect(url_for('final'))
        
    

    #get the mod field
    teamMod = proMod.query.filter_by(teamNumber=team_num).first()
    
    modFields = [ 
        teamMod.Intro, 
        teamMod.PartOne, 
        teamMod.PartTwo, 
        teamMod.PartThr,  
        teamMod.Outro 
    ] 

    forms = [None, P_Part(), P_Part(), P_Part_TD(), P_Part()]    
   
    if part_num == 0 or part_num == 4:
        form = P_InOut()
        try: 
            dicMod = ast.literal_eval(modFields[part_num])
        except:       
            dicMod = {         
            'Rec' : '', 
            'Tex' : '', 
            'Pic' : ''    
            }  
        image_file = S3_LOCATION + dicMod['Pic']
        audio_file = S3_LOCATION + dicMod['Rec']  
        image_file1 = None
        image_file2 = None
        q2_file = None
        q1_file = None     
    else:
        form = forms[pro_num]
        try: 
            dicMod = ast.literal_eval(modFields[part_num])
        except:     
            dicMod = {         
            'Rec' : '', 
            'Tex' : '', 
            'Pic' : '', 
            'Q1' : '', 
            'A1' : '',
            'QA1rec' : '',
            'Q2' : '',
            'A2' : '',       
            'QA2rec' : ''
            }    
        image_file = S3_LOCATION + dicMod['Pic']
        audio_file = S3_LOCATION + dicMod['Rec']
        q1_file = S3_LOCATION + dicMod['QA1rec']
        q2_file = S3_LOCATION + dicMod['QA2rec']

        image_file1 = S3_LOCATION + dicMod['A1']
        image_file2 = S3_LOCATION + dicMod['A2']
        

    
    try: 
        statList = ast.literal_eval(teamMod.Status)
    except:         
        statList = [ 0, 0, 0, 0, 0 ]    
   
    print ('dicMod:', dicMod)
    print ('statList:', statList)

    if form.validate_on_submit():
        if form.Pic.data:
            mark = str(part_num) + 'Pic'
            data_filename = upload_data(form.Pic.data, pro_num, team_num, mark) 
            dicMod['Pic'] = data_filename         
        if form.Rec.data:
            mark = str(part_num) + 'Rec'
            data_filename = upload_data(form.Rec.data, pro_num, team_num, mark) 
            dicMod['Rec'] = data_filename
        if form.Tex.data:            
            dicMod['Tex'] = form.Tex.data 
        
        if 4 > part_num > 0: 
            if form.Q1.data:
                dicMod['Q1'] = form.Q1.data
            if form.A1.data:
                try:
                    mark = str(part_num) + 'Pic2'
                    data_filename = upload_data(form.A1.data, pro_num, team_num, mark) 
                    dicMod['A1'] = data_filename
                except: 
                    dicMod['A1'] = form.A1.data                
            if form.QA1rec.data:
                mark = str(part_num) + 'QA1Rec'
                data_filename = upload_data(form.QA1rec.data, pro_num, team_num, mark) 
                dicMod['QA1rec'] = data_filename      

            if form.Q2.data:
                dicMod['Q2'] = form.Q2.data
            if form.A2.data:
                try:
                    mark = str(part_num) + 'Pic3'
                    data_filename = upload_data(form.A2.data, pro_num, team_num, mark) 
                    dicMod['A2'] = data_filename
                except: 
                    dicMod['A2'] = form.A2.data                 
            if form.QA2rec.data:
                mark = str(part_num) + 'QA2Rec'
                data_filename = upload_data(form.QA2rec.data, pro_num, team_num, mark) 
                dicMod['QA2rec'] = data_filename  
            

        if part_num == 0:
            teamMod.Intro = str(dicMod)
        elif part_num == 1:
            teamMod.PartOne = str(dicMod)
        elif part_num == 2:
            teamMod.PartTwo = str(dicMod)    
        elif part_num == 3:
            teamMod.PartThr = str(dicMod)
        elif part_num == 4:
            teamMod.Outro = str(dicMod)
        
        if '' in dicMod.values():
            statList[part_num] = 0  
        else:                
            statList[part_num] = 1

        teamMod.Status = str(statList)

        db.session.commit() 
        flash('Your project been updated', 'success')
        return redirect(request.url)
    elif request.method == 'GET':       
        form.Tex.data = dicMod['Tex']        
        if 4 > part_num > 0: 
            form.Q1.data = dicMod['Q1']
            form.A1.data = dicMod['A1']
            form.Q2.data = dicMod['Q2']
            form.A2.data = dicMod['A2']
   
    
    parts = ['Intro', 'Part 1','Part 2','Part 3','Ending']  

    context = {
        'form' : form,
        'image_file' : image_file,
        'image_file1' : image_file1,
        'image_file2' : image_file2, 
        'audio_file' : audio_file,  
        'title' : titles[pro_num],  
        'part' : parts[part_num],
        'part_num' : part_num,
        'complete' : statList[part_num], 
        'q2_file' : q2_file, 
        'q1_file' : q1_file, 

    }

    if pro_num == 3: 
        return render_template('project/project_destinations.html', **context)
    else: 
        return render_template('project/project_layout.html', **context)




@app.route ("/projtest/<int:pro_num>/<int:team_num>", methods=['GET','POST'])
@login_required
def project_test(pro_num, team_num):


    # exam mods will also be used later on
    examMods =[None, P1_EX, P2_EX, P3_EX, P4_EX]

    # query list found at the top
    if team_num == 0:     
        available = []    
        for row in queryList[pro_num]:
            if row.ProInt != 0:
                available.append(row.teamNumber)
        team_num = random.choice(available)        


    formList = [
        None, 
        P_Ans(),
        P_Ans(), 
        P_Ans3(), 
        P_Ans()
    ]

    form = formList[pro_num]

    formParts = {
        1 : [form.Part1, form.Part11, form.Part12], 
        2 : [form.Part2, form.Part21, form.Part22], 
        3 : [form.Part3, form.Part31, form.Part32], 
    }
    
    proMod = modList[pro_num]   

    #search model for team
    teamModel = proMod.query.filter_by(teamNumber=team_num).first()
    names = ast.literal_eval(teamModel.teamNames)

    users = {}
    for name in names:        
        image = User.query.filter_by(username=name).first().image_file        
        users[name] = [name, S3_LOCATION + image]
    
    start = 0
    if User.query.filter_by(id=1).first().projects == 1:
        start = 1
    elif User.query.filter_by(id=current_user.id).first().projects == 1:
        start = 1


    #restrict access to teammembers only
    if current_user.id == 1:
        pass
    elif start == 1:
        pass
    elif current_user.username not in names:
        flash('The exam has not started yet', 'danger')
        return redirect(url_for('final'))
    

    #get the mod field
    teamMod = proMod.query.filter_by(teamNumber=team_num).first()
    
    modFields = [ 
        teamMod.Intro, 
        teamMod.PartOne, 
        teamMod.PartTwo, 
        teamMod.PartThr,  
        teamMod.Outro 
    ]  

    dicModA = {         
            'Rec' : '', 
            'Tex' : '', 
            'Pic' : ''    
            }  
    
    dicModB = {         
            'Rec' : '', 
            'Tex' : '', 
            'Pic' : '', 
            'Q1' : '', 
            'A1' : '',
            'QA1rec' : '',
            'Q2' : '',
            'A2' : '',       
            'QA2rec' : ''
            }  

    dataDict = {
        0 : dicModA,
        1 : dicModB,
        2 : dicModB,
        3 : dicModB,
        4 : dicModB,
        5 : dicModA
    }

    for part in modFields:
        try: 
            liteval = ast.literal_eval(part)
            dataDict[modFields.index(part)] = liteval
        except: 
            pass

    
    model = examMods[pro_num]

    
    exam = model.query.filter_by(studentName=current_user.username).filter_by(projTeam=team_num).first()    

    if exam == None: 
        examStart = model(studentName=current_user.username, projTeam=team_num, status=str([0,0,0,0,0]))
        db.session.add(examStart)
        db.session.commit()  
        return redirect(url_for('project_test', pro_num=pro_num, team_num=team_num))

    status = ast.literal_eval(exam.status)  
    ansDict = { 
        0 : exam.Part0, 
        1 : [exam.Part1, exam.Part11, exam.Part12] , 
        2 : [exam.Part2, exam.Part21, exam.Part22] ,        
        3 : [exam.Part3, exam.Part31, exam.Part32] ,         
        4 : exam.Part4,
    } 

    print (ansDict) 

    if form.validate_on_submit():  
        if current_user.id == 1: 
            pass 
            # set to delete checks  
            model.query.filter_by(id=exam.id).delete()
            db.session.commit()
            return redirect(url_for('project_dash'))
        if form.Part0.data:
            exam.Part0 = form.Part0.data
            status[0] = 1
        if form.Part1.data and form.Part11.data and form.Part12:
            status[1] = 1
            exam.Part1 = form.Part1.data
            exam.Part11 = form.Part11.data
            exam.Part12 = form.Part12.data
        if form.Part2.data and form.Part21.data and form.Part22:
            status[2] = 1
            exam.Part2 = form.Part2.data
            exam.Part21 = form.Part21.data
            exam.Part22 = form.Part22.data
        if form.Part3.data and form.Part31.data and form.Part32:
            status[3] = 1
            exam.Part3 = form.Part3.data
            exam.Part31 = form.Part31.data
            exam.Part32 = form.Part32.data
        if form.Part4.data:
            status[4] = 1
            exam.Part4 = form.Part4.data
        exam.status = str(status)
        db.session.commit() 
        flash('Your test has been updated', 'success')
        return redirect(request.url)
    elif request.method == 'GET':
        pass
        
   
    
    context = {    
        'form' : form,    
        'title' : titles[pro_num],        
        'S3_LOCATION' : S3_LOCATION,
        'dataDict' : dataDict, 
        'ansDict' : ansDict,
        'team' : team_num, 
        'users' : users, 
        'formParts' : formParts,
        'QNA'  :  [None, 'QA1rec', 'QA2rec'], 
        'status' : status
    }

    if current_user.id == 1:        
        return render_template('project/project_inst.html', **context)
    elif pro_num == 3:
        return render_template('project/project_dest.html', **context)
    else:
        return render_template('project/project_test.html', **context)



