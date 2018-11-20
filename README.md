# Human versus Machine
<div align="center"><img src="app/static/logos/radai-machine-vs-man.svg.png" alt="Human versus Machine Artwork" width="40%"></div>

### Installation - Requirements
1. Python
2. Virtualenv
3. Mysql
4. Messaging service - stmp server
5. [Git Large File Storage (LFS) Client](https://packagecloud.io/github/git-lfs/install)


### Installation - Configuration

The application config files reside in  `config.py`.  In your directory you have a file named `config.py.example`
Edit the file to update your mysql username and password and the mailing stmp server (I use elasticemail.com) then rename the file as `config.py`


### Installation - Steps

1. Set up python
```$ python --version```

2. Set up your virtual environment in the project folder
```
$ pip install virtualenv
$ virtualenv ENV
$ source bin/activate  (for Linux or Mac OS ) - Else for Windows -
$ > \path\to\env\Scripts\activate
```

Get the source code
```
$ git clone https://gitlab.com/librehealth/RadAIJournal.git
$ cd RadAIJournal
$ virtualenv venv
$ source my_project/bin/activate  # For linux
$ venv\Scripts\activate.bat # for Windows
```


3. Install the python modules using the requirements file
```
$ pip install -r requirements.txt
```

### Getting the database ready

The application relies on a  mysql backend
**Note** : When working with database servers such as MySQL and PostgreSQL, you have to create the database in the database server before running upgrade.

In this case our database name is **radAI**
```
$ mysql -u  -p
$ mysql> CREATE DATABASE radAI;
```

To set this up on a new installation , delete the **migrations** folder  then run the following commands

```
$ python manage.py db init
$ python manage.py db migrate  #generates the migration script
$ python manage.py db upgrade  #Applies the changes to the database
```

### Email setup
Edit the following files in the config.py
```
MAIL_SERVER = 'smtp.elasticemail.com'
MAIL_PORT= 2525
MAIL_USERNAME = 'myusername'
MAIL_PASSWORD = 'mypassword'
MAIL_USE_TLS = False
```

### Finally running the application

Assumes that you have
1. Database migrations done
2. The environment with all the pip modules installed
3. Updated the config.py file with email setup/instructions

#### Linux / Mac
```
$ python radaijournal.py
```

Go to <a href="http://localhost:5000"> http://localhost:5000 </a>to access the application

### Contributors
1. Judy Gichoya
2. Avanigadda, Prem Chand
3. Siddhartha Nuthakki
4. Aaron Elson P - GCI student from 2017 who made the logo
5. Saptarshi Purkayastha
6. Priyanshu Sinha
7. Robby O'Connor - our dev ops master
