from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.debug = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)

login = LoginManager(app)
login.login_view = 'login'

Bootstrap(app)

from app import routes,models