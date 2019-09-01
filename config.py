import json
import os
from os import environ


class BaseConfig: 
    SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
    
    try:  
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']         
        DEBUG = False        
    except:
        #TravelEng DB
        SQLALCHEMY_DATABASE_URI = 'postgres://apomnzwugaszpu:d0dd4b8a4a0eb4afb54af960f6d6fbdf0c251344cd62c0aff157808a62222382@ec2-54-83-201-84.compute-1.amazonaws.com:5432/d40v3i8lgf43pl'
        MAIL_USERNAME = 'chrisflask0212@gmail.com'
        MAIL_PASSWORD = 'flask0212'
        DEBUG = True 
        
          



    
    
