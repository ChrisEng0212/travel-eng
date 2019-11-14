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


@app.route ("/final")
def final():

    queryList = [        
        P1_NM.query.all() 
        ] 

    titles = [
        None, 
        'At the Night Market', 
        'Around Taipei'
    ]

    projDict = {}
    count = 1 
    for modelQuery in queryList:
        for row in modelQuery:            
            if current_user.username in ast.literal_eval(row.teamNames):
                status = ast.literal_eval(row.Status)
                projDict[count] = [str(count), titles[count], ast.literal_eval(row.teamNames), str(row.teamNumber), status, sum(status)]        
        count += 1

    if test: 
        href = 'http://127.0.0.1:5000/project/'
    else: 
        href = 'https://travel-eng.herokuapp.com/project/'
    
    print (projDict)


    return render_template('project/final.html', projDict=projDict, href=href)
 

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
        P1_NM 
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
        15 : ['Peggy', 'Wei', 'Coral'],
        16: ['Felisia', 'Michelle', 'Jasmine']
    }

    #add the extra teams -->  dictionary = teamsDict --> manualAdd
    dictionary = teamsDict

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


@app.route ("/project/<int:pro_num>/<int:team_num>/<int:part_num>", methods=['GET','POST'])
@login_required
def project_build(pro_num, team_num, part_num):
    
    modList = [
        None,
        P1_NM 
        ]  
    proMod = modList[pro_num]   

    #search model for team
    teamModel = proMod.query.filter_by(teamNumber=team_num).first()
    names = ast.literal_eval(teamModel.teamNames)

    if current_user.id == 1:
        pass
    elif current_user.username not in names:
        return None # dashboard
    

    #get the mod field
    teamMod = proMod.query.filter_by(teamNumber=team_num).first()
    
    modFields = [ 
        teamMod.Intro, 
        teamMod.PartOne, 
        teamMod.PartTwo, 
        teamMod.PartThr,  
        teamMod.Outro 
    ]     
   
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
    else:
        form = P_Part()
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
                dicMod['A1'] = form.A1.data                
            if form.QA1rec.data:
                mark = str(part_num) + 'QA1Rec'
                data_filename = upload_data(form.QA1rec.data, pro_num, team_num, mark) 
                dicMod['QA1rec'] = data_filename      

            if form.Q2.data:
                dicMod['Q2'] = form.Q2.data
            if form.A2.data:
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
   
    titles = [
        None, 
        'At the NightMarket', 
        'Around Taipei'
    ]

    parts = ['Intro', 'Part 1','Part 2','Part 3','Ending']  

    context = {
        'form' : form,
        'image_file' : image_file, 
        'audio_file' : audio_file,  
        'title' : titles[pro_num],  
        'part' : parts[part_num],
        'part_num' : part_num,
        'complete' : statList[part_num], 
        'q2_file' : q2_file, 
        'q1_file' : q1_file, 

    }

    return render_template('project/project_layout.html', **context)


