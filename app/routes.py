#!/bin/python

import os
import pandas as pd

from flask import render_template,Blueprint,flash,redirect,url_for,send_from_directory,request
from flask_bootstrap import __version__ as FLASK_BOOTSRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_login import login_user, logout_user, current_user, login_required 
from werkzeug.urls import url_parse
from flask_mail import Mail, Message

from markupsafe import escape

from PIL import Image
from io import StringIO

from app import app, db
from app.forms import LoginForm, XrayForm, RegisterForm
from app.models import User, Report

mydata = pd.read_csv('app/static/FinalWorklist.csv')
mydata['img_index'] = mydata['img']
mydata.set_index('img_index',inplace=True)

#mail classes
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title= 'Nyumbani')

@app.route('/worklist')
@login_required
def worklist():
    #search the DB for all studies read by the current user 

    reports = Report.query.filter_by(user_id=current_user.id)
    cxr_read = []

    #are there any images returned 
    if reports.count > 0:
        for report in reports:
            cxr_read.append(report.img_id)  
        
        # Drop them from the dataframe before sampling them again to create the worklist 
        unread_cxr = mydata.drop(cxr_read)

    else:
        unread_cxr = mydata     

    #sample 20 studies from the list 
    myworklist = unread_cxr.sample(20)

    myworklist_data = []
    for index,row in myworklist.iterrows():
        mydict = {
            "img":row.img,
            "pt_id":row.pt_id,
            "study": "CXR",
            "age":row.age,
            "sex":row.sex
        }

        myworklist_data.append(mydict)

    return render_template('worklist.html',myworklist_data=myworklist_data)

@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

@app.route('/study/<img_id>',methods=['GET','POST'])
@login_required
def study(img_id):
    form = XrayForm()
    if request.method == 'GET':
        
        file_name = 'cxr/' + str(img_id) 
        
        #search for patient ID, Age and sex for the specific image we are rendering 
        img_data = mydata.loc[mydata['img'] == img_id]
        if len(img_data) > 0:
            #means there are metadata for that image 
            for index,row in img_data.iterrows():
                img_details = {
                    'pt_id' : row.pt_id,
                    'age' : row.age,
                    'sex' : row.sex
                }
        return render_template('study.html',user_image = file_name, image_details = img_details,img_id = img_id, form=form)
    elif request.method == 'POST':
        #validate that the forms data is correct 
        # Pneumonia must be selected
        if request.form.get('pneumonia'):
            _pneumonia = request.form.get('pneumonia')
        else:
            #pneumonia field was not selected 
            flash("Pneumonia diagnosis must be selected !",category="danger")
            return redirect(url_for('study',img_id = img_id))

        #now we have pneumonia we can check if other fields are present and save them
        if request.form.get('infiltrates'):
            infiltrates = request.form.get('infiltrates')
        else:
            infiltrates = '0'

        if request.form.get('consolidation'):
            consolidation = request.form.get('consolidation')
        else:
            consolidation = '0'

        if request.form.get('atelectasis'):
            atelectasis = request.form.get('atelectasis')
        else:
            atelectasis = '0'

        if request.form.get('comments'):
            comments = request.form.get('comments')
        else:
            comments = ''
        
        #get the ground truth and prediction for the img 
        img_data = mydata.loc[mydata['img'] == img_id]
        if len(img_data) > 0:
            #means there are metadata for that image 
            for index,row in img_data.iterrows():
                ground_truth = row.Pneumonia,
                prediction = row.Pneumonia_pred
                
        #save our cxr report
        try:
            report = Report(img_id = img_id, pneumonia = _pneumonia, consolidation=consolidation,
            infiltrates=infiltrates, atelectasis=atelectasis, comments=comments, user_id=current_user.id,
            ground_truth = ground_truth, prediction = prediction)

            db.session.add(report)
            db.session.commit()
            flash("Report saved successfully!", 'success')
        except:
            flash("CXR report was NOT saved successfully","danger")
            return redirect(url_for('study',img_id = img_id))

        return redirect(url_for('worklist'))

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password',category='danger')
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('worklist'))
    return render_template("login.html",title="Sign In", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/register3",methods=['GET','POST'])
def register3():
    form = RegisterForm(request.form)

    if request.method == 'GET':
        return render_template('register.html',form = form)

    elif request.method == 'POST':

        user_email = request.form.get('email')
        #check that length of email is not null
        if len(user_email) == 0:
            #means no email was entered 
            flash("Invalid email entered",category='danger')
            return redirect(url_for('register'))

        #search the database and ensure that there is no duplicate email 
        user = User.query.filter_by(email=user_email)
        ## TODO - verify the email
        """
        if user is not None:
            #duplicate email exists in the database 
            flash("Email exists in the database!",category='danger')
            return redirect(url_for('register'))
        """
        
        #Check both password fields match 
        password = request.form.get('password')
        if len(password) == 0:
            #means no password entered 
            flash("Invalid password entered",category='danger')
            return redirect(url_for('register'))
        elif (len(password) < 8  ):
            # password length is less than 8 chars 
            flash("Password must be 8 characters or more",category='danger')
            return redirect(url_for('register'))
        else:
            # check that this matches with password field 2 
            password2 = request.form.get('password2')
            if password != password2:
                flash("Passwords do not match!",category='danger')
                return redirect(url_for('register'))
        
        #prepare object to save 
        try:
            new_user = User(email=user_email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            #Activate user email now 
            token = generate_confirmation_token(user_email)
            msg = Message('WELCOME TO RAD vs MACHINE', sender = 'judy@joleh.com', recipients = [user_email])
            msg.body = "Thank you for registering in the RAD vs MACHINE competition"
            confirm_url = url_for('confirm_email',token=token,_external=True)
            #msg.html = render_template('activate.html',confirm_url=confirm_url)
            
            mail.send(msg)

            flash("User Account created successfully! Check email for activation instructions", 'success')
            return render_template('redirect.html')
        except:
            flash("User Account NOT created successfully","danger")
            return redirect(url_for('register'))

    return render_template('register.html',form = form)

@app.route("/register2", methods=['GET', 'POST'])
def register2():
    form = RegisterForm(request.form)
    if request.method == 'GET':
        return render_template('register.html',form = form)
    elif request.method == 'POST':
        print(form.data)

        if request.form.get('email'):
            user_email = request.form.get('email')

            #search the database and ensure that there is no duplicate email 
            emails = User.query.filter_by(email=user_email)
            if emails.count == 0:
                #means the user email is unique 
                pass
            elif emails.count > 0 :
                #duplicate email exists in the database 
                flash("Email exists in the database!",category='danger')
                return redirect(url_for('register'))
        
        
        # Get first name
        if request.form.get('first_name'):
            user_first_name = request.form.get('first_name')
        else:
            user_first_name = ''

        # Get middle name
        if request.form.get('middle_name'):
            user_middle_name = request.form.get('middle_name')
        else:
            user_middle_name = ''

        # Get last name 
        if request.form.get('last_name'):
            user_last_name = request.form.get('last_name')
        else:
            user_last_name = ''

        #Get NPI 
        if request.form.get('npi'):
            user_npi = request.form.get('npi')

            # search for NPIs in the database 
            npis = User.query.filter_by(npi=user_npi)
            if npis.count == 0:
                #means unique NPI 
                pass
            else:
                flash("NPI exists in the database!",category='danger')
                return redirect(url_for('register'))

        #Get doctor quals 
        doctor = request.form.get('doctor')

        # Get radiologist 
        radiologist = request.form.get('radiologist')

        # Get training 
        training = request.form.get('training')

        # Get years of clinical practice 
        practice = request.form.get('clinical_practice')

        # Get institution type 
        institution = request.form.get('institution_type')

        # Get clinical_speciality
        specialty = request.form.get('clinical_specialty')

        # country 
        country = request.form.get('country')

        #state 
        state = request.form.get('')
        
        return render_template('register.html',form = form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404