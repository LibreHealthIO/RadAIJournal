from datetime import datetime
from app import db, login 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(80),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    remember_me = db.Column(db.Boolean)
    date_registered = db.Column(db.DateTime,index=True,default=datetime.utcnow)

    def __repr__(self):
        return 'User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class UserProfile(db.Model):
    profile_id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(160))
    middle_name = db.Column(db.String(160))
    last_name = db.Column(db.String(160))
    npi = db.Column(db.Integer,unique=True)
    doctor = db.Column(db.String(32))
    radiologist = db.Column(db.String(32))
    training = db.Column(db.String(32))
    clinical_practice = db.Column(db.String(32))
    clinical_specality = db.Column(db.String(32))
    institution_type = db.Column(db.String(32))
    country = db.Column(db.String(32))
    state = db.Column(db.String(32))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    img_id = db.Column(db.String(320),index=True)
    pneumonia = db.Column(db.String(32),index=True)
    consolidation = db.Column(db.String(32))
    infiltrates = db.Column(db.String(32))
    atelectasis = db.Column(db.String(32))
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    ground_truth = db.Column(db.Integer)
    prediction = db.Column(db.Integer)

    def __repr__(self):
        return 'Report {}>'.format(self.id)

    

