import json
import os
from os import environ

### Note: need to store credential as environment variable later!!!!
### http://zabana.me/notes/upload-files-amazon-s3-flask.html



configDict = {
    'titleColor':'#db0b77',
    'bodyColor':'#fff0fa', 
    'headTitle':'Travel English Course', 
    'S3_LOCATION':'https://travel-eng.s3.ap-northeast-1.amazonaws.com/',
    'S3_BUCKET_NAME':'travel-eng'    
    }    



class BaseConfig: 
    SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
 
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']    
    
    DEBUG = True 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True    
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    
    
