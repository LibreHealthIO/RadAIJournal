from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators, BooleanField, SubmitField, RadioField, SelectMultipleField, TextField, SelectField, FloatField, widgets , IntegerField
from wtforms.validators import DataRequired, Length , EqualTo , Email , NumberRange , ValidationError

from app.models import User , UserProfile
from luhn import verify

class LoginForm(FlaskForm):
    email = StringField('Email address',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    confirm = StringField('Confirm')
    submit = SubmitField('Sign In')

class XrayForm(FlaskForm):
    pneumonia = StringField('Pneumonia Diagnosis',validators=[DataRequired()])
    consolidation = StringField('Consolidation')
    infiltrates = StringField('Infiltrates')
    atelectasis = StringField('Atelectasis')
    comments = TextField('Comments')
    submit = SubmitField('Save Report')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 64)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class RegForm(FlaskForm):
    first_name = StringField('First Name :',[validators.Length(min=1, max=50),validators.DataRequired()])
    middle_name = StringField('Middle Name :')
    last_name = StringField('Last Name :',[validators.Length(min=1, max=50),validators.DataRequired()])
    npi= StringField('NPI :')
    doctor = SelectField('Are you a doctor ?', [validators.DataRequired()], choices=[('a', 'MD/DO'), ('b', 'MBBS'), ('c', 'MBchB'),('d', 'I am not a doctor')])
    radiologist = RadioField('Are you a radiologist ?',choices=[('yes', 'Radiologist'), ('no', 'Non Radiologist'),('N/A','N/A')])
    training = SelectField('What is your level of training ?', choices=[('staff','Staff'),('r0','Resident-R0/PGY 1'),('r1','Resident-R1/PGY 2'),('r2','Resident-R2/PGY 3'),('r3','Resident-R3/PGY 4'),('r4','Resident-R4/PGY 5'),('N/A','N/A')])
    clinical_practice = RadioField('How many years have you been in clinical practice ?',choices=[('a', '<5 years'),('b', '5-10 years'),('c', '10-15 years'),('d', '15-20 years'),('e', '>20 years'),('N/A','N/A')])
    clinical_specialty = MultiCheckboxField('What is your clinical specialty?', choices=[('Body_Abdomen','Body/Abdomen'),('Head_Neck','Head and Neck'),('Nuclear_Medicine','Nuclear Medicine'),('MSK','MSK'),('Pediatrics','Pediatrics'),('Breast','Breast'),('Chest_Cardiac','Chest/Cardiac'),('Interventional_Radiology','Interventional Radiology'),('ER_General','ER/General'),('N/A','N/A')])
    institution_type = RadioField('Institution type',choices=[('private', 'Private practice'), ('academic', 'Academic'),('N/A','N/A')])
    submit = SubmitField('submit')
    
    def validate_npi(self, npi):
        user = UserProfile.query.filter_by(npi=npi.data).first()
        if npi.data == "0000000000" :
            return True
        else:
            if user is None:
                if npi_is_valid(npi.data):
                    return True
                else:
                    raise ValidationError('This NPI number is invalid.')
                    return False
            else:
                raise ValidationError('This NPI number is already used.')
                return False
            

def npi_is_valid(npi):
    LUHN_PREFIX = "80840"
    prefixed_number = "%s%s" % (LUHN_PREFIX, npi)
    return verify(prefixed_number)
    