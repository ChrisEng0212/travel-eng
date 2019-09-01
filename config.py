import json
import os
from os import environ
try:
    from aws import Settings
    DATABASE = Settings.SQLALCHEMY_DATABASE_URI
except:
    pass


class BaseConfig: 
    SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
    
    try:  
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']         
        DEBUG = os.environ['DEBUG'] 
        print ('Config_Success')        
    except:        
        SQLALCHEMY_DATABASE_URI = DATABASE
        MAIL_USERNAME = 'chrisflask0212@gmail.com'
        MAIL_PASSWORD = 'flask0212'
        DEBUG = True 
        
          



    
    
