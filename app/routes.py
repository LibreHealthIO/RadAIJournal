#!/bin/python

import os
import pandas as pd

from flask import render_template,Blueprint,flash,redirect,url_for,send_from_directory,request
from flask_bootstrap import __version__ as FLASK_BOOTSRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_login import login_user, logout_user, current_user, login_required 
from werkzeug.urls import url_parse

from markupsafe import escape

from PIL import Image
from io import StringIO

from app import app, db
from app.forms import LoginForm, XrayForm
from app.models import User,Report

mydata = pd.read_csv('app/static/FinalWorklist.csv')
mydata['img_index'] = mydata['img']
mydata.set_index('img_index',inplace=True)

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'gichoya'}
    posts = [
        {
            'author' : {'username':'John'},
            'body':'Beautiful day in Portland!'
        },
        {
            'author' : {'username':'Susan'},
            'body':'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title= 'Nyumbani',user = user,posts=posts)

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
        user = User.query.filter_by(username=form.username.data).first()
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

@app.route("/register")
def register():
    return(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404