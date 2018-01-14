import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #used to protect against CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #SQLite configurations 
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """

    #MYSQL COnfigs
    SQLALCHEMY_DATABASE_URI = 'mysql://root:manmano@localhost/radAI'
