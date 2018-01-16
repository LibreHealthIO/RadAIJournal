import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #used to protect against CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECURITY_PASSWORD_SALT = 'you-will-never-guess'

    MAIL_SERVER = 'smtp.elasticemail.com'
    MAIL_PORT= 2525
    MAIL_USERNAME = 'yourusername'
    MAIL_PASSWORD = 'password'
    MAIL_USE_TLS = False

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

