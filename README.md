### Installation - Requirements 
1. Python 
2. Virtualenv 
3. Mysql 


### Configuration 

The application config files reside in  ```config.py```
Edit the file to update your mysql username and password

### Installation - Steps

1. Set up python 
```
$ python --version
```

2. Set up your virtual environment in the project folder
```
$ pip install virtualenv
$ git clone https://gitlab.com/librehealth/RadAIJournal.git
$ cd RadAIJournal
$ virtualenv venv

source my_project/bin/activate
```

3. Install the python modules using the requirements file

```
pip install -r requirements.txt

```

### Getting the database ready 

The application relies on a  mysql backend 
**Note** : When working with database servers such as MySQL and PostgreSQL, you have to create the database in the database server before running upgrade.

In this case our database name is radAI
```
mysql -u  -p

mysql> CREATE DATABASE radAI;

```

To set this up on a new installation , delete the **migrations** folder  then run the following commands

```
FLASK_APP=radaijournal.py
flask db init
flask db migrate  #generates the migration script 
flask db upgrade  #Applies the changes to the database 
```


### Finally running the application 

Assumes that you have 
1. Database migrations done 
2. The environment with all the pip modules installed 
3. Updated the config.py file 

```
FLASK_APP=radaijournal.py
flask run
```

Go to localhost:5000 to access the application

### Contributors 
1. Judy Gichoya 