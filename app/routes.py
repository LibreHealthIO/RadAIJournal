#!/bin/python

import os

from flask import render_template,Blueprint,flash,redirect,url_for,send_from_directory
from flask_bootstrap import __version__ as FLASK_BOOTSRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape

from PIL import Image
from io import StringIO

from app import app

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
def worklist():
    return render_template('worklist.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/study/<study_id>')
def study(study_id):
    studyid = study_id
    #img = Image.new('RGB',"/Users/judywawira/Programming/RadAIJournal/00006484_000.png")
    #file_name = "/Users/judywawira/Programming/RadAIJournal/00006484_000.png"
    file_name = "00006484_000.png"
    return render_template('study.html',study_id=studyid,user_image = file_name)
    #return serve_pil_image(img)
    #return send_from_directory('/Users/judywawira/Programming/RadAIJournal','00006484_000.png')