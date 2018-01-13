import os 

class Config(object):
    #used to protect against CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'