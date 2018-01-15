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
    SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/radAI'

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'user'
    MYSQL_PASSWORD = 'password'
    MYSQL_DB = 'radAI'

