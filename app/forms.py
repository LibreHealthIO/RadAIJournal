from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectMultipleField,TextField
from wtforms.validators import DataRequired,Length 

data = [('2','consolidation'),
        ('3','infiltrates'),
        ('4','atelectasis')]

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=8, message="The password needs to be at least 8 characters long")])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class XrayForm(FlaskForm):
    pneumonia = RadioField('Pneumonia Diagnosis',choices=[('1','Diagnostic of Pneumonia'),('0','Negative for pneumonia')],validators=[DataRequired()])
    findings = SelectMultipleField("Select all applicable diagnosis",choices=data, validators=[DataRequired()])
    comments = TextField('Comments')
    submit = SubmitField('Save Report')
