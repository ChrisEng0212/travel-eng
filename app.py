from flask import Flask, render_template   #app = Flask(__name__)
#from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy  #needed for app initialization (see below - db)
from flask_bcrypt import Bcrypt  #needed for password storage
from flask_login import LoginManager, current_user #needed for login
from flask_mail import Mail
#from config import Config

#value = User.query.filter_by(username).first()   

app = Flask(__name__)
#app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = 'login' # if user isn't logged in it will redirect to login page
login_manager.login_message_category = 'info'
mail = Mail(app)

SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
SQLALCHEMY_DATABASE_URI = 'postgres://apomnzwugaszpu:d0dd4b8a4a0eb4afb54af960f6d6fbdf0c251344cd62c0aff157808a62222382@ec2-54-83-201-84.compute-1.amazonaws.com:5432/d40v3i8lgf43pl'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True    
#MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
#MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")



from routesUser import *
from routesAdmin import *


if __name__ == '__main__': 
    app.run(debug=True)
    
    