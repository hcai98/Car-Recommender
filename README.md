# MSiA423 ALT - An Automobile Recommender

Author: Haoyang (Bill) Cai

QA: Qianyin Cao, Kunhang Luo

## Table of Contents
* [Project Charter ](#Project-charter)
  * [Vision](#Vision)
  * [Mission](#Mission)
  * [Success criteria](#Success-criteria)
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
  * [1. Initialize the database ](#1.-Initialize-the-database)
  * [2. Configure Flask app ](#2.-Configure-Flask-app)
  * [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)
* [Mypy](#Mypy)
* [Pylint](#Pylint)

## Project charter

### Vision

Due to the ongoing semiconductor shortage, the post-pandemic automotive market suffers from supply shortages. With car prices stuck in high gear, many buyers can no longer afford their dream cars with the pre-pandemic budget and must turn to other options. However, this raises a simple yet hard-to-answer question in many buyers' minds: What Then?

`ALT` (short for "alternative") aims to help potential buyers efficiently find alternative options by recommending cars similar to the dream car they've always wanted yet could no longer get in today's market. Countless hours and days that buyers would have wasted on browsing, researching, and test driving cars that don't match their expectation could now be saved using this recommender app.

###  Mission

Users will first specify the *make* and *model* of their dream car. The app will then *sequentially output cars* similar to the given input based on an unsupervised clustering algorithm ((users must click "interested" or "not interested" to go to the next recommendation). The recommender is facilitated by a publicly available dataset called [DVM-CAR](https://deepvisualmarketing.github.io/).

**Example:** A user who has initially been looking for a BMW 3-Series is looking for other options in the market. Based characteristics of the given car, the app would first output the most similar car (say Audi A4) along with its specs and images. The user would then click "interested" or "not interested" to go to the next recommendation car. The process is repeated until the whole recommendation list is exhausted.

Based on the recommendations, users would be able to narrow down their search and utilize time more efficiently.

###  Success criteria

#### Machine Learning Metrics

The ideal clustering algorithm/architecture will be picked using evaluation metrics such as Pseudo F and Silhouette Statistics. To be deployed, the best model should achieve an **R-Squared** greater than or equal to 0.75. 

#### Business Metrics

The app is designed so that user must click "interested" or "not interested" to view the next recommended car. We can use the user's selections to compute the Satisfaction Rate of our recommendations (number of likes / number of recommendations). To be deemed successful, the app should have **Averaged Satisfaction Rate per User** greater than 0.2. 

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile.run                <- Dockerfile for building image to execute run.py  
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app 

### 1. Initialize the database 
#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.run -t pennylanedb .
```
#### Create the database 
To create the database in the location configured in `config.py` run: 

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb create_db  --engine_string=sqlite:///data/tracks.db
```
The `--mount` argument allows the app to access your local `data/` folder and save the SQLite database there so it is available after the Docker container finishes.


#### Adding songs 
To add songs to the database:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb ingest --engine_string=sqlite:///data/tracks.db --artist=Emancipator --title="Minor Cause" --album="Dusk to Dawn"
```

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2022-msia423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.app -t pennylaneapp .
```

This command builds the Docker image, with the tag `pennylaneapp`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.

#### Running the app

To run the Flask app, run: 

```bash
 docker run --name test-app --mount type=bind,source="$(pwd)"/data,target=/app/data/ -p 5000:5000 pennylaneapp
```
You should be able to access the app at http://127.0.0.1:5000/ in your browser (Mac/Linux should also be able to access the app at http://127.0.0.1:5000/ or localhost:5000/) .

The arguments in the above command do the following: 

* The `--name test-app` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5000:5000` argument maps your computer's local port 5000 to the Docker container's port 5000 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill test-app 
```
where `test-app` is the name given in the `docker run` command.

If you did not name the container, you can look up its name by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

## Testing

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.test -t pennylanetest .
```

To run the tests, run: 

```bash
 docker run pennylanetest
```

The following command will be executed within the container to run the provided unit tests under `test/`:  

```bash
python -m pytest
```

## Mypy

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.mypy -t pennymypy .
```

To run mypy over all files in the repo, run: 

```bash
 docker run pennymypy .
```
To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennymypy .
```

To run mypy for a single file, run: 

```bash
 docker run pennymypy run.py
```

## Pylint

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.pylint -t pennylint .
```

To run pylint for a file, run:

```bash
 docker run pennylint run.py 
```

(or any other file name, with its path relative to where you are executing the command from)

To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennylint run.py
```
