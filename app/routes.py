#!/bin/python

import os
import pandas as pd
import pymysql
import numpy as np

from flask import Flask, render_template, Blueprint, flash, redirect, url_for, send_from_directory, request, session, logging , abort
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from flask_bootstrap import __version__ as FLASK_BOOTSRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from markupsafe import escape

from PIL import Image
from io import StringIO

from sqlalchemy import create_engine, update

from app import app, db
from app.forms import LoginForm, XrayForm, RegisterForm, RegForm
from app.models import User, Report, StatsTable, UserProfile

#pandas for rendering worklists
mydata = pd.read_csv('app/static/FinalWorklist.csv')
mydata['img_index'] = mydata['img']
mydata.set_index('img_index', inplace=True)

#Mail variables
mail = Mail(app)


#mail classes
def generate_confirmation_token(email):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=600):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  try:
    email = serializer.loads(
        token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
  except:
    return False
  return email


# Check if user logged in
def is_logged_in(f):

  @wraps(f)
  def wrap(*args, **kwargs):
    #print(session)
    if 'login_user' in session:
      return f(*args, **kwargs)
    else:
      flash('Unauthorized, Please register and Confrim your email', 'danger')
      return redirect(url_for('register'))

  return wrap


@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='Human v/s Machine')


@app.route('/worklist')
@is_logged_in
def worklist():
  #search the DB for all studies read by the current user
  try:
    reports = Report.query.filter_by(user_id=current_user.id)
  except:
    flash("Cannot connect to the database, contact support", "danger")
    return redirect(url_for('worklist'))

  reports_count = reports.count()
  cxr_read = []

  #are there any images returned
  if reports_count > 0:
    for report in reports:
      cxr_read.append(report.img_id)

    # Drop them from the dataframe before sampling them again to create the worklist
    unread_cxr = mydata.drop(cxr_read)

  else:
    unread_cxr = mydata

  #sample 20 studies from the list
  myworklist = unread_cxr.sample(20)

  myworklist_data = []
  for index, row in myworklist.iterrows():
    mydict = {
        "img": row.img,
        "pt_id": row.pt_id,
        "study": "CXR",
        "age": row.age,
        "sex": row.sex
    }

    myworklist_data.append(mydict)

  return render_template('worklist.html', myworklist_data=myworklist_data)


@app.route('/stats')
@is_logged_in
def stats():
  #Should not show stats to a user with an incomplete profile
  try:
    profile = UserProfile.query.filter_by(user_id=current_user.id)
  except:
    flash("Database connection error , contact support", "danger")
    return redirect(url_for('stats'))

  if profile.count() == 0:
    #no profile for user
    flash(
        "You need to complete your profile to view the leaderboard and results",
        "info")
    return redirect(url_for('profile'))

  #declare some variables
  score = 0
  ground_truth = []
  prediction = []
  pneumonia = []

  #Query the report table
  try:
    reports = Report.query.filter_by(user_id=current_user.id)
  except:
    flash(
        'Unable to connect to the database , contact support',
        category='danger')
    return redirect(url_for('stats'))

  if reports.count() > 0:
    for report in reports:
      ground_truth.append(int(report.ground_truth))
      prediction.append(int(report.prediction))
      pneumonia.append(int(report.pneumonia))

    #now create a dataframe with results
    df = pd.DataFrame({
        'ground_truth': ground_truth,
        'prediction': prediction,
        'Pneumonia': pneumonia
    })

    conditions1 = [
        (df['ground_truth'] == df['prediction']) &
        (df['Pneumonia'] == df['ground_truth']),  #Machine n human were right
        (df['ground_truth'] != df['prediction']) &
        (df['Pneumonia'] != df['ground_truth']),  #Both were wrong
        (df['ground_truth'] == df['prediction']) &
        (df['Pneumonia'] != df['ground_truth']),  #Machine right, human wrong
        (df['ground_truth'] != df['prediction']) &
        (df['Pneumonia'] == df['ground_truth'])
    ]  #Machine wrong, human right
    choices1 = [0, 0, -1, 1]

    conditions2 = [
        (df['Pneumonia'] == df['ground_truth']),  #Check human accuracy
        (df['Pneumonia'] != df['ground_truth'])
    ]  #Check human accuracy
    choices2 = [1, 0]

    conditions3 = [
        (df['ground_truth'] == df['prediction']),  #Check machine accuracy
        (df['ground_truth'] != df['prediction'])
    ]  #Check machine accuracy
    choices3 = [1, 0]

    df['individual scores'] = np.select(conditions1, choices1, default=np.nan)
    df['Human Accuracy'] = np.select(conditions2, choices2, default=np.nan)
    df['Machine Accuracy'] = np.select(conditions3, choices3, default=np.nan)

    Total = sum(df['individual scores'])
    Human_accuracy = (sum(df['Human Accuracy'] / len(df))) * 100
    machine_accuracy = (sum(df['Machine Accuracy'] / len(df))) * 100

    try:
      stats_table = StatsTable.query.filter_by(user_id=current_user.id)
    except:
      flash(
          'Unable to connect to the database , contact support',
          category='danger')
      return redirect(url_for('stats'))

    if stats_table.count() > 0:
      try:
        db.session.query(StatsTable).filter_by(user_id=current_user.id).update({
            "total":
            Total,
            "human_accuracy":
            Human_accuracy,
            "machine_accuracy":
            machine_accuracy
        })
        db.session.commit()
      except:
        flash(
            'Unable to connect to the database , contact support',
            category='danger')
        return redirect(url_for('stats'))
    else:
      try:
        stats_table = StatsTable(
            user_id=current_user.id,
            total=Total,
            human_accuracy=Human_accuracy,
            machine_accuracy=machine_accuracy)
        db.session.add(stats_table)
        db.session.commit()
      except:
        flash(
            'Unable to connect to the database , contact support',
            category='danger')
        return redirect(url_for('stats'))

  #Fetch stats
  try:
    leader_table = db.session.query(StatsTable).filter().order_by(
        StatsTable.total.desc()).limit(5)
  except:
    flash(
        'Unable to connect to the database , contact support',
        category='danger')
    return redirect(url_for('stats'))

  total_dummy = []
  human_dummy = []
  machine_dummy = []
  user_dummy = []

  Total = 0
  Human_accuracy = 0
  machine_accuracy = 0

  leader_board = pd.DataFrame()

  for i in leader_table:
    user_dummy.append(int(i.user_id))
    total_dummy.append(i.total)
    human_dummy.append(int(i.human_accuracy))
    machine_dummy.append(int(i.machine_accuracy))

    leader_board = pd.DataFrame({
        'user': user_dummy,
        'total': total_dummy,
        'human_accuracy': human_dummy,
        'machine_accuracy': machine_dummy
    })
  return render_template(
      'stats.html',
      data=[current_user.id, Total, Human_accuracy, machine_accuracy],
      leader_board=leader_board)


@app.route('/study/<img_id>', methods=['GET', 'POST'])
@is_logged_in
def study(img_id):
  form = XrayForm()
  if request.method == 'GET':

    try:
      file_name = 'cxr/' + str(img_id)
      #search for patient ID, Age and sex for the specific image we are rendering
      img_data = mydata.loc[mydata['img'] == img_id]
      if len(img_data) > 0:
        #means there are metadata for that image
        for index, row in img_data.iterrows():
          img_details = {'pt_id': row.pt_id, 'age': row.age, 'sex': row.sex}
      return render_template(
          'study.html',
          user_image=file_name,
          image_details=img_details,
          img_id=img_id,
          form=form)
    except:
      abort(404) # return 404 on wrong image id
  
  elif request.method == 'POST':
    #validate that the forms data is correct
    # Pneumonia must be selected
    if request.form.get('pneumonia'):
      _pneumonia = request.form.get('pneumonia')
    else:
      #pneumonia field was not selected
      flash("Pneumonia diagnosis must be selected !", category="danger")
      return redirect(url_for('study', img_id=img_id))

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
      for index, row in img_data.iterrows():
        ground_truth = row.Pneumonia,
        prediction = row.Pneumonia_pred

    #save our cxr report
    try:
      report = Report(
          img_id=img_id,
          pneumonia=_pneumonia,
          consolidation=consolidation,
          infiltrates=infiltrates,
          atelectasis=atelectasis,
          comments=comments,
          user_id=current_user.id,
          ground_truth=ground_truth,
          prediction=prediction)

      db.session.add(report)
      db.session.commit()
      flash("Report saved successfully!", 'success')
    except:
      flash("CXR report was NOT saved successfully", "danger")
      return redirect(url_for('study', img_id=img_id))

    return redirect(url_for('worklist'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password', category='danger')
      return redirect(url_for('login'))
    if user.confirm == 'NO':
      flash(
          'Unconfirmed account, Please check your mail to confirm',
          category='danger')
      return redirect(url_for('login'))
    if not user.check_password(form.password.data):
      flash("Invalid password", 'danger')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    session['login_user'] = True
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('index')
    return redirect(url_for('worklist'))
  return render_template("login.html", title="Sign In", form=form)


@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
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

    #save user
    db.session.add(user)
    db.session.commit()
    flash(
        'Congratulations, you are now a registered user!. Check your email to confirm your account',
        'success')

    #generate email token
    email = form.email.data
    token = generate_confirmation_token(email)
    msg = Message(
        'WELCOME TO HUMAN vs MACHINE COMPETITION',
        sender='judy@joleh.com',
        recipients=[email])
    msg.body = "Hello Flask message sent from Flask-Mail"
    confirm_url = "https://radai.club/confirm/%s" % token
    # confirm_url = url_for('confirm_email', token=token, _external=True)
    msg.html = render_template('activate.html', confirm_url=confirm_url)
    mail.send(msg)

    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
  #check if currently logged in user has a profile
  try:
    profile = UserProfile.query.filter_by(user_id=current_user.id)
  except:
    flash("Cannot connect to the database , contact support", "danger")
    return redirect(url_for('profile'))

  if profile.count() > 0:
    #means profile is already existing
    flash("You have an existing profile saved profile on file", "info")
    return redirect(url_for('index'))

  form = RegForm(request.form)
  if form.validate_on_submit():
    first_name = form.first_name.data
    middle_name = form.middle_name.data
    last_name = form.last_name.data
    npi = form.npi.data
    doctor = form.doctor.data
    radiologist = form.radiologist.data
    training = form.training.data
    clinical_practice = form.clinical_practice.data
    clinical_specialty = form.clinical_specialty.data
    clinical_specialty = ''.join(clinical_specialty)
    institution_type = form.institution_type.data
    country = request.form['country']
    state = request.form['state']
    userProfile = UserProfile(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        npi=npi,
        doctor=doctor,
        radiologist=radiologist,
        training=training,
        clinical_practice=clinical_practice,
        clinical_specialty=clinical_specialty,
        institution_type=institution_type,
        country=country,
        state=state,
        user_id=current_user.id)

    #save to DB
    try:
      db.session.add(userProfile)
      db.session.commit()
      flash('User profile saved successfully', 'success')
      return redirect(url_for('worklist'))
    except:
      flash('Failed to save user profile !', 'danger')
      return redirect(url_for('profile'))

    return redirect(url_for('worklist'))
  return render_template('profile.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404


@app.route('/confirm/<token>')
def confirm_email(token):
  try:
    email = confirm_token(token)
  except:
    flash('Invalid link', 'danger')
  else:
    user = User.query.filter_by(email=email).first()
    user.confirm = 'YES'
    db.session.commit()
    session['user_email'] = email
    flash('Your account activation was successful!', 'success')
    return redirect(url_for('login'))


@app.route('/about')
def about():
  return render_template('about.html')
