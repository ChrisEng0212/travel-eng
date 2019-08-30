import json
import os

### Note: need to store credential as environment variable later!!!!
### http://zabana.me/notes/upload-files-amazon-s3-flask.html



class Config: 
    SECRET_KEY = '145d4a32162599ef6f426668b77f2d9a' #This will protect the app against cookies. We need it for using forms, correctly. 
    #SQLALCHEMY_DATABASE_URI = 'postgres://apomnzwugaszpu:d0dd4b8a4a0eb4afb54af960f6d6fbdf0c251344cd62c0aff157808a62222382@ec2-54-83-201-84.compute-1.amazonaws.com:5432/d40v3i8lgf43pl'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True    
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    
    
