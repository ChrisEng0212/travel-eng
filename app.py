from flask import Flask, render_template   #app = Flask(__name__)
#from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy  #needed for app initialization (see below - db)
from flask_bcrypt import Bcrypt  #needed for password storage
from flask_login import LoginManager, current_user #needed for login
from flask_mail import Mail
import os



app = Flask(__name__)
app.config.from_object('config.BaseConfig')
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = 'login' # if user isn't logged in it will redirect to login page
login_manager.login_message_category = 'info'

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'chrisflask0212',
    MAIL_PASSWORD = 'flask0212',
))

mail = Mail(app)


from routesUser import *
from routesAdmin import *


if __name__ == '__main__': 
    app.run()
    #(debug=True)
    
    