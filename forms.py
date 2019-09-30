from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed, FileRequired # what kind of files are allowed to be uploaded
from flask_login import current_user # now we can use this for the account update
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField, validators, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from models import *  


class Attend(FlaskForm):
    attend = RadioField('Attendance', choices = [('On time', 'On time'), ('Late', 'Late')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])                  
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count') 
    role =  RadioField('What role would you like today?', choices = [('work', 'TravelAgent'), ('cust', 'Traveller')])                                                
    submit = SubmitField('Join')

class AttendLate(FlaskForm):
    attend = RadioField('Attendance', choices = [('Late', 'Late'), ('2nd Class', '2nd Class')])
    name =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID (9 numbers)', validators=[DataRequired(), Length(9)])                  
    teamnumber = IntegerField ('Team Number')
    teamcount = IntegerField ('Team Count')
    role =  RadioField('What role would you like today?', choices = [('work', 'TravelAgent'), ('cust', 'Traveller')])                                                
    submit = SubmitField('Join')

class AttendInst(FlaskForm):
    attend = StringField ('Notice')   
    username =  StringField ('Name in English', validators=[DataRequired(), Length(min=2, max=20)])
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(9)])                  
    teamnumber = IntegerField ('Status') 
    teamcount = IntegerField ('Team Count')   
    teamsize = IntegerField ('Team Size (0 for no teams)')  
    unit = StringField ('unit(2) eg 01 or MT', validators=[DataRequired(), Length(min=2, max=20)])                                         
    submit = SubmitField('Join')

class RegistrationForm(FlaskForm):

    username = StringField ('Name in English', 
                                validators=[DataRequired(), Length(min=2, max=20)])    
    studentID = StringField ('Student ID (9 numbers)', 
                                validators=[DataRequired(), Length(9)])
    email = StringField('Email', 
                                validators=[DataRequired(), Email()])  
    device = RadioField('Main Device', 
                                choices = [('Apple', 'Apple iphone'), ('Android', 'Android Phone'), ('Win', 'Windows Phone')])                                
    password = PasswordField('Password', 
                                validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password',  
                                        validators=[DataRequired(), EqualTo('password')] )
    submit = SubmitField('Join')

    def validate_username(self, username):  # the field is username
        user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
        if user:  # meaning if True
            raise ValidationError('Another student has that username, please add family name')  # ValidationError needs to be imported from wtforms
    
    def validate_email(self, email): 
        user = User.query.filter_by(email=email.data).first()  
        if user:  
            raise ValidationError('That email has an account already, did you forget your password?') 

    def validate_studentID(self, studentID):  
        try:
            int(studentID.data)
        except:
            raise ValidationError('9 numbers; no S')
        user = User.query.filter_by(studentID=studentID.data).first()  
        if user:           
            raise ValidationError('That student ID already has an account, did you forget your password?')
        

class LoginForm(FlaskForm):
    studentID = StringField ('Student ID', validators=[DataRequired(), Length(9)])     
    password = PasswordField('Password', validators=[DataRequired()]) 
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotForm(FlaskForm):
    email = StringField ('Email', validators=[DataRequired(), Email()])         
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, email): 
        user = User.query.filter_by(email=email.data).first()  
        if user is None:  
            raise ValidationError('There is no account with that email, contact your instructor') 

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()] )
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')] )
    submit = SubmitField('Set New Password')

class UpdateAccountForm(FlaskForm):
    #username = StringField ('Username', validators=[DataRequired(), Length(min=2, max=20)])    
    email = StringField('Email', validators=[DataRequired(), Email()] )   
    picture = FileField ('Change Profile Picture', validators=[FileAllowed(['jpg', 'png'])]) 
    submit = SubmitField('Update')

    def validate_username(self, username):  # the field is username
        if username.data != current_user.username: # if the updated one is the same then no need to validate
            user = User.query.filter_by(username=username.data).first()  #User was imported at the top # first means just find first instance?
            if user:  # meaning if True
                raise ValidationError('That user name has been used already, please add another letter')  # ValidationError needs to be imported from wtforms
    
    def validate_email(self, email):  
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()  
            if user:  
                raise ValidationError('That email has an account already, did you forget your password?')  
    
    def validate_studentID(self, studentID):  
        if studentID.data != current_user.student.ID:
            user = User.query.filter_by(studentID=studentID.data).first()  
            if user:  
                raise ValidationError('That student ID already has an account, did you forget your password?')  


class MidtermSetUp(FlaskForm):    
    MT01 = RadioField (label='Number of students in team', choices = [('2', '2'), ('3', '3')])
    MT02 = RadioField (label='Role Play Format', choices=[('Travel Prep (2)', 'Travel Prep (2)'), ('Travel Agent (2)','Travel Agent (2)'), 
    ('Travel Agent (3)','Travel Agent (3)'), ('Immigration (3)','Immigration (3)'), ('Hotel (3)','Hotel (3)'), ('Taxi(2)','Taxi(2)')])
    MT03 = StringField (label='Student ID 1', validators=[DataRequired(), Length(9)]) 
    MT04 = StringField (label='Student ID 2', validators=[DataRequired(), Length(9)])
    MT05 = StringField (label='Student ID 3 (if only 2 students then use 000000000)', validators=[DataRequired(), Length(9)], default='000000000') 
    
    Submit = SubmitField('Submit')

    def validate_MT03(self, MT03):         
        if MT03.data != current_user.studentID:          
            raise ValidationError('This should be your student ID') 
        

    def validate_MT04(self, MT04):        
        user = User.query.filter_by(studentID=MT04.data).first()        
        if user:
            pass
        else:
            raise ValidationError('That student ID does not exist') 

    def validate_MT05(self, MT05):        
        if MT05.data == '000000000':
            pass
        else:
            user = User.query.filter_by(studentID=MT05.data).first()        
            if user:
                pass
            else:
                raise ValidationError('That student ID does not exist') 

class MidtermDetails(FlaskForm):        
    
    MT06 = StringField (label='Link to your script') 
    MT07 = StringField (label='Link to your video')
    
    MT08 = StringField (label='Question 1')
    MT09 = StringField (label='Question 2')
    MT10 = StringField (label='Question 3')
    MT11 = StringField (label='Question 4')
    
    MT12 = StringField (label='Answer 1')
    MT13 = StringField (label='Answer 2')
    MT14 = StringField (label='Answer 3')
    MT15 = StringField (label='Answer 4')

    Submit = SubmitField('Submit')

class MidtermExample(FlaskForm):     
    
    A01 = StringField (label='Q1')
    A02 = StringField (label='Q2')
    A03 = StringField (label='Q3')
    A04 = StringField (label='Q4')    

    Submit = SubmitField('Submit')

#### Agent Conversations
AgentOne = {
    '1a' : ['Hi, ', 
    ['How can I help you today?', 'How can I help you today?'],
    ['What I can I help you with today?', 'What I can I help you with today?'],
    ['What can I do for you today?' ,'What can I do for you today?']       
    ],
    '1b' : ['I have some vacation time coming up and ',
        ['stress-free', 'I just want a stress-free holiday.'], 
        ['good value','I need a good value package.'], 
        ['no time','I don’t have time to organize a trip']
    ],
    '2a' : ['Okay, ', 
    ['How long do you have off work?', 'How long do you have off work?'],
    ['How long do you have for vacation?','How long do you have for vacation?'],
    ['How long is your break?','How long is your break?']     
    ],
    '2b' : ['Well, ',
        ['5 days', 'I just have a 5 day break'], 
        ['8 days', 'I have 8 days off work'], 
        ['10 days','Just the first 10 days in July'], 
        ['16 days','Its about 16 days']
    ],
    '3a' : ['Great, that’s a nice amount of time. ',
    ['Where would you like to go?','Where would you like to go?'],
    ['Where did you have in mind?','Where did you have in mind?'],
    ['Have you thought about a destination?','Have you thought about a destination?']
    ],    
    '3b' : ['Actually, I would love to spend time ',
        ['nature', 'in nature'], 
        ['city','in a big city'], 
        ['ocean','close to the ocean']
    ],
    '4a' : ['Have you considered........',   
        ['Nature: Hokkaido - City: Bangkok - Ocean: Bali', 'Nature: Hokkaido - City: Bangkok - Ocean: Bali'], 
        ['Nature: Chang Mai - City: Tokyo - Ocean: Okinawa','Nature: Chang Mai - City: Tokyo - Ocean: Okinawa'], 
        ['Nature: Guilin - City: Seoul - Ocean: Phuket', 'Nature: Guilin - City: Seoul - Ocean: Phuket']        
    ],
    '4b' : ['Okay, ', 
        ['Sounds good', 'Sounds good'], 
        ['Sounds perfect','Sounds perfect'], 
        ['Sounds great','Sounds great']               
    ],
    '5a' : ['No problem, ',
        ['So what kind of place would like to stay in?','So what kind of place would like to stay in?'],
        ['So what about your accommodation?', 'So what about your accommodation?'],
        ['So what kind of accommodation would you like?', 'So what kind of accommodation would you like?']
    ],    
    '5b' : ['For my accomodation, ',
        ['nothing too fancy', 'I don’t want anything too fancy.'], 
        ['just comfortable', 'I just want to be comfortable.'],
        ['taken care of','I want everything to be taken care of.'], 
        ['by myself','I like to do things by myself']
    ],
    'xx' : ['Okay... ',
    ['nothing too fancy -- ', 'perhaps a small guest house would suit you.'],   
    ['just comfortable -- ', 'we can recommend a decent hotel.'],
    ['taken care of -- ','there is an all-inclusive resort that you might like.'], 
    ['by myself -- ','we could look into renting an apartment in the area.']
    ],
    
    '6b' : ['Thanks, before I go can I ask about ',
        ['visa requirements', 'the visa requirements'], 
        ['car rental','the car rental options'], 
        ['local tours','local tours on offer']
    ],
    '6a' : ['Certainly, ',
    ['We will find out what the options are available','We will find out what options are available'],
    ['I’ll check the information and get back to you','I’ll check the information and get back to you'],
    ['I will prepare the details for you','I will prepare the details for you']        
    ],  
}


class AgentListen(FlaskForm): 
    C01 = RadioField (label='What is the customers situation?', choices=[
            (AgentOne['1b'][1][1], AgentOne['1b'][1][0]), 
            (AgentOne['1b'][2][1], AgentOne['1b'][2][0]), 
            (AgentOne['1b'][3][1], AgentOne['1b'][3][0])
        ]) 
    C02 = RadioField (label='C02', choices=[
            (AgentOne['2b'][1][1], AgentOne['2b'][1][0]), 
            (AgentOne['2b'][2][1], AgentOne['2b'][2][0]), 
            (AgentOne['2b'][3][1], AgentOne['2b'][3][0]),
            (AgentOne['2b'][4][1], AgentOne['2b'][4][0])
        ]) 
    C03 = RadioField (label='C03', choices=[
            (AgentOne['3b'][1][1], AgentOne['3b'][1][0]), 
            (AgentOne['3b'][2][1], AgentOne['3b'][2][0]), 
            (AgentOne['3b'][3][1], AgentOne['3b'][3][0])
        ]) 
    C04 = RadioField (label='C04', choices=[
            (AgentOne['4b'][1][1], AgentOne['4b'][1][0]), 
            (AgentOne['4b'][2][1], AgentOne['4b'][2][0]), 
            (AgentOne['4b'][3][1], AgentOne['4b'][3][0])
        ]) 
    C05 = RadioField (label='C05', choices=[
            (AgentOne['5b'][1][1], AgentOne['5b'][1][0]), 
            (AgentOne['5b'][2][1], AgentOne['5b'][2][0]), 
            (AgentOne['5b'][3][1], AgentOne['5b'][3][0]),
            (AgentOne['5b'][4][1], AgentOne['5b'][4][0])
        ]) 
    C06 = RadioField (label='C06', choices=[
            (AgentOne['6b'][1][1], AgentOne['6b'][1][0]), 
            (AgentOne['6b'][2][1], AgentOne['6b'][2][0]), 
            (AgentOne['6b'][3][1], AgentOne['6b'][3][0])           
        ]) 
    Submit = SubmitField('Submit')

class AgentCustomer(FlaskForm): 
    A01 = RadioField (label=AgentOne['1b'][0], choices=[
            (AgentOne['1b'][1][1], AgentOne['1b'][1][1]), 
            (AgentOne['1b'][2][1], AgentOne['1b'][2][1]), 
            (AgentOne['1b'][3][1], AgentOne['1b'][3][1])
        ]) 
    A02 = RadioField (label=AgentOne['2b'][0], choices=[
            (AgentOne['2b'][1][1], AgentOne['2b'][1][1]), 
            (AgentOne['2b'][2][1], AgentOne['2b'][2][1]), 
            (AgentOne['2b'][3][1], AgentOne['2b'][3][1]),
            (AgentOne['2b'][4][1], AgentOne['2b'][4][1])
        ])  
    A03 = RadioField (label=AgentOne['3b'][0], choices=[
            (AgentOne['3b'][1][1], AgentOne['3b'][1][1]), 
            (AgentOne['3b'][2][1], AgentOne['3b'][2][1]), 
            (AgentOne['3b'][3][1], AgentOne['3b'][3][1])
        ]) 
    A04 = RadioField (label=AgentOne['4b'][0], choices=[
            (AgentOne['4b'][1][1], AgentOne['4b'][1][1]), 
            (AgentOne['4b'][2][1], AgentOne['4b'][2][1]), 
            (AgentOne['4b'][3][1], AgentOne['4b'][3][1])
        ]) 
    A05 = RadioField (label=AgentOne['5b'][0], choices=[
            (AgentOne['5b'][1][1], AgentOne['5b'][1][1]), 
            (AgentOne['5b'][2][1], AgentOne['5b'][2][1]), 
            (AgentOne['5b'][3][1], AgentOne['5b'][3][1]),
                (AgentOne['5b'][4][1], AgentOne['5b'][4][1])
        ]) 
    A06 = RadioField (label=AgentOne['6b'][0], choices=[
            (AgentOne['6b'][1][1], AgentOne['6b'][1][1]), 
            (AgentOne['6b'][2][1], AgentOne['6b'][2][1]), 
            (AgentOne['6b'][3][1], AgentOne['6b'][3][1]),
               
        ])     
    Submit = SubmitField('Submit')

class AgentWorker(FlaskForm): 
    A01 = RadioField (label=AgentOne['1a'][0], choices=[
            (AgentOne['1a'][1][1], AgentOne['1a'][1][1]), 
            (AgentOne['1a'][2][1], AgentOne['1a'][2][1]), 
            (AgentOne['1a'][3][1], AgentOne['1a'][3][1])
        ]) 
    A02 = RadioField (label=AgentOne['2a'][0], choices=[
            (AgentOne['2a'][1][1], AgentOne['2a'][1][1]), 
            (AgentOne['2a'][2][1], AgentOne['2a'][2][1]), 
            (AgentOne['2a'][3][1], AgentOne['2a'][3][1])
        ])  
    A03 = RadioField (label=AgentOne['3a'][0], choices=[
            (AgentOne['3a'][1][1], AgentOne['3a'][1][1]), 
            (AgentOne['3a'][2][1], AgentOne['3a'][2][1]), 
            (AgentOne['3a'][3][1], AgentOne['3a'][3][1])
        ])     
    A04 = RadioField (label=AgentOne['4a'][0], choices=[
            (AgentOne['4a'][1][1], AgentOne['4a'][1][1]), 
            (AgentOne['4a'][2][1], AgentOne['4a'][2][1]), 
            (AgentOne['4a'][3][1], AgentOne['4a'][3][1])
        ]) 
    A05 = RadioField (label=AgentOne['5a'][0], choices=[
            (AgentOne['5a'][1][1], AgentOne['5a'][1][1]), 
            (AgentOne['5a'][2][1], AgentOne['5a'][2][1]), 
            (AgentOne['5a'][3][1], AgentOne['5a'][3][1])
        ])  
    A06 = RadioField (label=AgentOne['6a'][0], choices=[
            (AgentOne['6a'][1][1], AgentOne['6a'][1][1]), 
            (AgentOne['6a'][2][1], AgentOne['6a'][2][1]), 
            (AgentOne['6a'][3][1], AgentOne['6a'][3][1])
    ])  
      
    Submit = SubmitField('Submit')  

           

class Project(FlaskForm):
    Title = TextAreaField (label='Project Title')    
    TextOne = TextAreaField (label='Speaking Text One', validators=[DataRequired(message='Please write your answers')])    
    PictureOne = FileField (label='Picture One', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordOne = FileField (label='Record One', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    TextTwo  = TextAreaField (label='Speaking Text Two ', validators=[DataRequired(message='Please write your answers')])    
    PictureTwo  = FileField (label='Picture Two ', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordTwo  = FileField (label='Record Two ', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    TextThree = TextAreaField (label='Speaking Text Three', validators=[DataRequired(message='Please write your answers')])    
    PictureThree = FileField (label='Picture Three', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordThree = FileField (label='Record Three', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    TextFour = TextAreaField (label='Speaking Text Four', validators=[DataRequired(message='Please write your answers')])    
    PictureFour = FileField (label='Picture Four', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordFour = FileField (label='Record Four', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    TextFive = TextAreaField (label='Speaking Text Five', validators=[DataRequired(message='Please write your answers')])    
    PictureFive = FileField (label='Picture Five', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordFive = FileField (label='Record Five', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    TextSix = TextAreaField (label='Speaking Text Six', validators=[DataRequired(message='Please write your answers')])    
    PictureSix = FileField (label='Picture Six', validators=[FileAllowed(['jpg', 'png'], message="Please upload jpeg/png image")])
    RecordSix = FileField (label='Record Six', validators=[FileAllowed(['mp3', 'm4a', 'mp4'], message="Please upload mp3/m4a/mp4")])
    Complete = RadioField('Attendance', choices = [('No, not yet', 'No, not yet'), ('Yes, please check', 'Yes, please check')], default='No, not yet')
    Stage = IntegerField ('Team Number')
    Submit = SubmitField('Submit')


