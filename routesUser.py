import sys
import boto3
import random
import os
import time
import datetime
from datetime import timedelta
from sqlalchemy import asc, desc
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from forms import *
from models import *
import ast

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


def midtermCalculate():
    grades = MidGrades.query.filter_by(username=current_user.username).first()

    if grades.cpg != None:
        cpg = round(grades.cpg / 18 * 50)
    else:
        cpg = 0

    mtrm = MidTerm.query.all()
    mtDict = {}
    for mt in mtrm:
        mtDict[mt.id] = [mt.teamMemOne,
                         mt.teamMemTwo, mt.teamMemThr, mt.checkQue]

    proj = 'None'
    for key in mtDict:
        if current_user.studentID in mtDict[key]:
            proj = 'Done'

    mAns = MidAnswers.query.all()

    ansDict = {}
    for ans in mAns:
        try:
            ansDict[ans.username].add(ans.examID)
        except:
            ansDict[ans.username] = {None}
            ansDict[ans.username].add(ans.examID)
            ansDict[ans.username].discard(None)

    if current_user.id == 1:
        for key in ansDict:
            grades = MidGrades.query.filter_by(username=key).first()
            grades.mvg = len(ansDict[key])
            db.session.commit()
    try:
        vids = len(ansDict[current_user.username])
    except:
        vids = 0

    return None


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if current_user.is_authenticated:
        attLog = AttendLog.query.filter_by(
            username=current_user.username).all()
    else:
        attLog = None

    attDict = {}
    for log in attLog:
        attDict[log] = [log.date_posted +
                        timedelta(hours=8), log.attend, log.attScore, log.extraStr]

    midterm = current_user.midterm / 2 

    projList = ast.literal_eval(current_user.course)

    return render_template('instructor/home.html', title='home', attLog=attLog, attDict=attDict, midterm=midterm, projList=projList)


# Attendance //////////////////////////////////////////////
@app.route("/attend_team", methods=['GET', 'POST'])
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
            attendance = Attendance(username='Chris',
                                    attend='Notice', teamnumber=97, studentID='100000000')
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance is not open yet, please try later', 'danger')
            return redirect(url_for('home'))
        else:  # openData has return None
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
        teammates = Attendance.query.filter_by(
            teamnumber=fields.teamnumber).all()
        for teammate in teammates:
            image = User.query.filter_by(
                username=teammate.username).first().image_file
            users[teammate.username] = [teammate.username, S3_LOCATION + image]
    else:
        users = None

    # prepare initial form
    if count == 0:
        print('xxxxxxxxx')
        if form.validate_on_submit():

            # check last id for AttendLog
            lastID = AttendLog.query.order_by(desc(AttendLog.id)).first().id
            # team maker

            # role control
            #wCount = Attendance.query.filter_by(role='work').count()
            # if form.role.data == 'work':
            # if wCount > 21:
            #flash('Sorry, there are too many HOTEL CLERKS already. Please choose HOTEL GUEST', 'info')
            # return redirect(url_for('att_team'))

            attendance = Attendance(username=form.name.data,
                                    attend=form.attend.data, teamnumber=form.teamnumber.data,
                                    teamcount=form.teamcount.data, studentID=form.studentID.data, unit=lastID+1)  # role=form.role.data
            db.session.add(attendance)
            db.session.commit()
            # long term log
            if form.attend.data == 'On time':
                attScore = 3
            elif form.attend.data == 'Late':
                attScore = 2
            else:
                attScore = 1
            attendLog = AttendLog(username=form.name.data,
                                  attend=form.attend.data, teamnumber=form.teamnumber.data,
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

    # after attendance is complete teamnumber 0 is reassigned to a team
    elif fields.teamnumber == 0:
        # { 1 : 1,  2 : 1  ,  3 :  0 }
        teamDict = {}
        for i in range(1, teamcount+1):
            count = Attendance.query.filter_by(teamnumber=i).count()
            if count:
                teamDict[i] = count
            else:
                teamDict[i] = 0
        print(teamDict)

        # all teams are full so make a new team
        if teamDict[teamcount] == teamsize:
            countField = Attendance.query.filter_by(username='Chris').first()
            countField.teamcount = teamcount + 1
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


@app.route("/course", methods=['GET', 'POST'])
@login_required
def course():
    sources = Sources.query.order_by(asc(Sources.date)).all()
    return render_template('student/course.html', sources=sources)
