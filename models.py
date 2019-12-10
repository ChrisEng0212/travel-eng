from datetime import datetime, timedelta
from app import app, db, login_manager
# this imports current user, authentication, get id (all the login attributes)
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

modListUnits = [None]


# login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username = db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    teamsize = db.Column(db.Integer)
    teamcount = db.Column(db.Integer)
    unit = db.Column(db.String(9))
    role = db.Column(db.String)


class AttendLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username = db.Column(db.String, nullable=False)
    studentID = db.Column(db.String(9), nullable=False)
    attend = db.Column(db.String)
    teamnumber = db.Column(db.Integer)
    attScore = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)


class User(db.Model, UserMixin):  # import the model
    # kind of value and the key unique to the user
    id = db.Column(db.Integer, primary_key=True)
    # must be a unique name and cannot be null
    username = db.Column(db.String(20), unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # images will be hashed to 20 and images could be the same
    image_file = db.Column(db.String(), nullable=False,
                           default='profiles/default.PNG')
    password = db.Column(db.String(60), nullable=False)
    device = db.Column(db.String(), nullable=False)
    attendance = db.Column(db.Integer)
    projects = db.Column(db.Integer)
    midterm = db.Column(db.Integer)
    exam = db.Column(db.Integer)
    course = db.Column(db.String)

    def get_reset_token(self, expires_sec=1800):
        expires_sec = 1800
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  # tell python not to expect that self parameter as an argument, just accepting the token
    def verify_reset_token(token):
        expires_sec = 1800
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):  # double underscore method or dunder method, marks the data, this is how it is printed
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Sources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    unit = db.Column(db.String)
    date = db.Column(db.DateTime)
    topic = db.Column(db.String)
    goalOne = db.Column(db.String)
    goalTwo = db.Column(db.String)
    activity = db.Column(db.String)
    linkOne = db.Column(db.String)
    linkTwo = db.Column(db.String)
    embed = db.Column(db.String)
    openSet = db.Column(db.Integer)
    extraStr = db.Column(db.String)
    extraInt = db.Column(db.Integer)

############### PROJECT MODELS ###################################


class MidTerm(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    teamNum = db.Column(db.String)
    vidOption = db.Column(db.String)
    teamMemOne = db.Column(db.String)
    teamMemTwo = db.Column(db.String)
    teamMemThr = db.Column(db.String)

    scrLink = db.Column(db.String)
    vidLink = db.Column(db.String)

    qOne = db.Column(db.String)
    aOne = db.Column(db.String)
    qTwo = db.Column(db.String)
    aTwo = db.Column(db.String)
    qThr = db.Column(db.String)
    aThr = db.Column(db.String)
    qFor = db.Column(db.String)
    aFor = db.Column(db.String)

    checkQue = db.Column(db.Integer)
    checkScr = db.Column(db.Integer)
    checkVid = db.Column(db.Integer)

    names = db.Column(db.String)
    duplicate = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class MidAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    A01 = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    username = db.Column(db.String)
    grade = db.Column(db.Integer)
    examID = db.Column(db.Integer)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class MidGrades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username = db.Column(db.String, unique=True, nullable=False)
    studentID = db.Column(db.String(9), unique=True, nullable=False)
    cpg = db.Column(db.Integer)
    mvg = db.Column(db.Integer)
    cpg_comments = db.Column(db.String)
    mvg_comments = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


### IMMIG ####################

class ImmigTrav(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A01x = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class ImmigOffr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A01x = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class ImmigList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    C01 = db.Column(db.String)
    C02 = db.Column(db.String)
    C03 = db.Column(db.String)
    C04 = db.Column(db.String)
    C05 = db.Column(db.String)
    C06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    match = db.Column(db.String)
    name = db.Column(db.String)
    extraStr = db.Column(db.String)

### IMMIG ####################


class HotelGuest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    A07 = db.Column(db.String)
    A08 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class HotelClerk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    A07 = db.Column(db.String)
    A08 = db.Column(db.String)
    A09 = db.Column(db.String)
    A10 = db.Column(db.String)
    A11 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class HotelList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    C01 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    match = db.Column(db.String)
    name = db.Column(db.String)
    extraStr = db.Column(db.String)

### Travel Agent ####


class AgentCust(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class AgentWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    A01 = db.Column(db.String)
    A02 = db.Column(db.String)
    A03 = db.Column(db.String)
    A04 = db.Column(db.String)
    A05 = db.Column(db.String)
    A06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    extraStr = db.Column(db.String)


class AgentList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    C01 = db.Column(db.String)
    C02 = db.Column(db.String)
    C03 = db.Column(db.String)
    C04 = db.Column(db.String)
    C05 = db.Column(db.String)
    C06 = db.Column(db.String)
    extraInt = db.Column(db.Integer)
    match = db.Column(db.String)
    name = db.Column(db.String)
    extraStr = db.Column(db.String)


class BaseProjects(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    teamNames = db.Column(db.String)
    teamNumber = db.Column(db.Integer, unique=True)
    Intro = db.Column(db.String)
    PartOne = db.Column(db.String)
    PartTwo = db.Column(db.String)
    PartThr = db.Column(db.String)
    Outro = db.Column(db.String)
    Status = db.Column(db.String)
    ProInt = db.Column(db.Integer)
    ProStr = db.Column(db.String)


class P1_NM(BaseProjects):
    id = db.Column(db.Integer, primary_key=True)


class P2_TA(BaseProjects):
    id = db.Column(db.Integer, primary_key=True)

class P3_TD(BaseProjects):
    id = db.Column(db.Integer, primary_key=True)

class P4_HT(BaseProjects):
    id = db.Column(db.Integer, primary_key=True)

class BaseExams(db.Model):
    __abstract__ = True
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    studentName = db.Column(db.String)
    projTeam = db.Column(db.Integer)
    Part0 = db.Column(db.String)
    Part1 = db.Column(db.String)
    Part11 = db.Column(db.String)
    Part12 = db.Column(db.String)
    Part2 = db.Column(db.String)
    Part21 = db.Column(db.String)
    Part22 = db.Column(db.String)
    Part3 = db.Column(db.String)
    Part31 = db.Column(db.String)
    Part32 = db.Column(db.String)
    Part4 = db.Column(db.String)
    status = db.Column(db.String)
    ExtraStr = db.Column(db.String)
    ExtraInt = db.Column(db.Integer)


class P1_EX(BaseExams):
    id = db.Column(db.Integer, primary_key=True)


class P2_EX(BaseExams):
    id = db.Column(db.Integer, primary_key=True)

class P3_EX(BaseExams):
    id = db.Column(db.Integer, primary_key=True)

class P4_EX(BaseExams):
    id = db.Column(db.Integer, primary_key=True)


class Info ():
    modListUnits = modListUnits


class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.id == 1:
                return True
            else:
                return False
        else:
            return True


admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Attendance, db.session))
admin.add_view(MyModelView(AttendLog, db.session))
admin.add_view(MyModelView(Sources, db.session))
admin.add_view(MyModelView(MidTerm, db.session))
admin.add_view(MyModelView(MidAnswers, db.session))
admin.add_view(MyModelView(MidGrades, db.session))
admin.add_view(MyModelView(P1_NM, db.session))
admin.add_view(MyModelView(P2_TA, db.session))
admin.add_view(MyModelView(P3_TD, db.session))
admin.add_view(MyModelView(P4_HT, db.session))
admin.add_view(MyModelView(P1_EX, db.session))
admin.add_view(MyModelView(P2_EX, db.session))
admin.add_view(MyModelView(P3_EX, db.session))
admin.add_view(MyModelView(P4_EX, db.session))

#admin.add_view(MyModelView(AgentCust, db.session))
#admin.add_view(MyModelView(AgentWork, db.session))
#admin.add_view(MyModelView(AgentList, db.session))
#admin.add_view(MyModelView(ImmigTrav, db.session))
#admin.add_view(MyModelView(ImmigOffr, db.session))
#admin.add_view(MyModelView(ImmigList, db.session))
#admin.add_view(MyModelView(HotelGuest, db.session))
#admin.add_view(MyModelView(HotelClerk, db.session))
#admin.add_view(MyModelView(HotelList, db.session))

for unit in modListUnits:
    if unit is None:
        pass
    else:
        admin.add_view(MyModelView(unit, db.session))
