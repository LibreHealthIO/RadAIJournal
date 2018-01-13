### Installation - Requirements 

You can use 
1. Pip 

```
pip install -r requirements.txt
```

2. Anaconda  

```
conda env create -f flask.yml
```

### Configuration 

The application config files reside in  ```config.py```

### Getting the database ready 

```
FLASK_APP=radaijournal.py
flask db init
flask db migrate  #generates the migration script 
flask db upgrade  #Applies the changes to the database 
```

**Note** : When working with database servers such as MySQL and PostgreSQL, you have to create the database in the database server before running upgrade.

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

### Some data references 

```
data = [('2','consolidation'),
        ('3','infiltrates'),
        ('4','atelectasis')]

        1 = pneumonia 
```