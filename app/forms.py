from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectMultipleField,TextField
from wtforms.validators import DataRequired,Length 

data = [('2','consolidation'),
        ('3','infiltrates'),
        ('4','atelectasis')]

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class XrayForm(FlaskForm):
    pneumonia = StringField('Pneumonia Diagnosis',validators=[DataRequired()])
    consolidation = StringField('Consolidation')
    infiltrates = StringField('Infiltrates')
    atelectasis = StringField('Atelectasis')
    comments = TextField('Comments')
    submit = SubmitField('Save Report')
