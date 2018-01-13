#!/bin/python

import os

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

def serve_pil_image(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

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
    return render_template('worklist.html')

@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

@app.route('/study/<study_id>')
@login_required
def study(study_id):
    studyid = study_id
    form = XrayForm()
    file_name = "00006484_000.png"
    return render_template('study.html',study_id=studyid,user_image = file_name,form=form)

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
        return redirect(next_page)
    return render_template("login.html",title="Sign In", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
