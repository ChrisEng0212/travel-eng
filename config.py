import json
import os
from os import environ


class BaseConfig: 
    SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True         

    try:  
        print('SUCCESS?')  
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] 
        print('SUCCESS1')
        MAIL_USERNAME = os.environ['GMAIL_SMTP_USER']
        print('SUCCESS2')
        MAIL_PASSWORD = os.environ['GMAIL_SMTP_PASSWORD']
        print('SUCCESS3')
        DEBUG = False
        print('SUCCESS')
    except:
        #TravelEng DB
        SQLALCHEMY_DATABASE_URI = 'postgres://apomnzwugaszpu:d0dd4b8a4a0eb4afb54af960f6d6fbdf0c251344cd62c0aff157808a62222382@ec2-54-83-201-84.compute-1.amazonaws.com:5432/d40v3i8lgf43pl'
        MAIL_USERNAME = 'chrisflask0212@gmail.com'
        MAIL_PASSWORD = 'flask0212'
        DEBUG = True 
        
          



    
    
