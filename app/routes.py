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
from app.models import User

mydata = pd.read_csv('app/static/FinalWorklist.csv')

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
    #mydata = pd.read_csv('app/static/FinalWorklist.csv')

    #sample 20 studies from the list 
    myworklist = mydata.sample(20)

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

        return render_template('study.html',user_image = file_name, image_details = img_details,
            form=form)
        #return render_template('study.html',study_id=studyid,user_image = file_name,form=form)
    elif request.method == 'POST':
        pass

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
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