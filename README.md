# ALT - An Automobile Recommender

Author: Haoyang (Bill) Cai

## Table of Contents
- [ALT - An Automobile Recommender](#msia423-alt---an-automobile-recommender)
  - [Table of Contents](#table-of-contents)
  - [Project charter](#project-charter)
    - [Vision](#vision)
    - [Mission](#mission)
    - [Success criteria](#success-criteria)
      - [Machine Learning Metrics](#machine-learning-metrics)
      - [Business Metrics](#business-metrics)
  - [Directory structure](#directory-structure)
  - [Envrionment Setup](#envrionment-setup)
    - [Environment Variables](#environment-variables)
      - [AWS Credential](#aws-credential)
      - [S3 Bucket](#s3-bucket)
      - [Database](#database)
    - [Docker Images](#docker-images)
  - [Data Acquasition](#data-acquasition)
  - [Modeling Pipeline](#modeling-pipeline)
    - [1. Download Data From S3](#1-download-data-from-s3)
    - [2. Data Cleaning](#2-data-cleaning)
    - [3. Create training features](#3-create-training-features)
    - [4. Train the model](#4-train-the-model)
    - [5. Label the data](#5-label-the-data)
    - [6. Model Evaluation](#6-model-evaluation)
  - [Load Data Into Database](#load-data-into-database)
    - [Create the database](#create-the-database)
      - [Ingest Data Into Database](#ingest-data-into-database)
  - [Running the app](#running-the-app)
      - [Kill the container](#kill-the-container)
  - [Testing](#testing)

## Project charter

### Vision

Due to the ongoing semiconductor shortage, the post-pandemic automotive market continues to suffer from supply shortages. With car prices stuck in high gear, many buyers can no longer afford their dream cars with the pre-pandemic budget and must turn to other options. However, this raises a simple yet hard-to-answer question in many buyers' minds: What Then?

`ALT` (short for "alternative") aims to help potential buyers efficiently find alternative options by recommending cars similar to the dream car they've always wanted yet could no longer get in today's market. Countless hours and even days that buyers would have wasted on browsing, researching, and test driving cars that don't match their expectation could now be saved using this recommender app.

###  Mission

Users will first specify the *make* and *model* of their dream car. The app will then *sequentially output* cars similar to the given input based on an unsupervised clustering algorithm (users must click "interested" or "not interested" to go to the next recommendation). The recommender is built using a publicly available dataset called [DVM-CAR](https://deepvisualmarketing.github.io/).

**Example:** A user who has initially been looking for a BMW 3-Series is looking for other options in the market. Based on characteristics of the given car, the app would output a list of cars that are the most similar to the user's dream car.

Based on the recommendations, users would be able to narrow down their search and utilize time more efficiently.

###  Success criteria

#### Machine Learning Metrics

The ideal clustering algorithm/architecture will be picked using Silhouette Statistics. To be deployed, the best model should achieve an ***Silhouette*** greater than or equal to 0.5.

#### Business Metrics

The app is designed so that user must click "interested" or "not interested" to view the next recommended car. We can use the user's selections to compute the Satisfaction Rate of our recommendations (number of likes / number of recommendations). To be deemed successful, the app should have ***Averaged Satisfaction Rate per User*** greater than 0.2. 

## Directory structure 

```
├── README.md                         <- You are here
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── dbconfig.py                   <- Configurations for run_db.py 
│   ├── flaskconfig.py                <- Configurations for Flask API 
│   ├── modelconfig.py                <- Configurations for run_model.py
│
├── data                              <- Folder that contains data used or generated.
│   ├── evaluation/                   <- Model evaluation results
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── processed/                    <- The processed data resulting from the modeling pipeline 
│   ├── raw/                          <- The raw data downloaded from the S3 bucket
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile                    <- Dockerfile for building image to run modeling pipeline
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
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
├── tests/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Envrionment Setup

### Environment Variables

#### AWS Credential
To set up the AWS credential, run the following commands with your own credential filled in. This is crucial for accessing the S3 bucket.
```shell
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
```

#### S3 Bucket
You will also need to provide the name of your S3 bucket to perform the data acquisition step.
```shell
export S3_BUCKET="s3://YOUR_BUCKET_NAME"
```

#### Database
The app's functioning depends on real-time access to a SQL data base. Run the following commands
with the URI of the SQL engine you desire.
```shell
export SQLALCHEMY_DATABASE_URI = "YOUR_DATABASE_URI"
```

### Docker Images
You will need to build the following three docker images to run the modeling pipeline and web app.
```shell
make image-model
make image-app
make image-test
```

## Data Acquasition
Run the following command to upload the source data to your S3 bucket. You may configure the path of the source file by changing the `SOURCEDATA_PATH` variable in the `Makefile`.

```shell
make raw-to-s3
```

## Modeling Pipeline

### 1. Download Data From S3
To download the raw data from your S3 Bucket, run the following commands
```shell
make acquire-from-s3
```
### 2. Data Cleaning
To clean the raw data, run 
```shell
make cleaned
```

### 3. Create training features
Once you obtained the cleaned data, run the following command to generate training features.
```shell
make features
```

### 4. Train the model
This command allows you to cluster the data using KMeans based on the generated features. Cluster centroid will be saved to a specified directory.
```shell
make trained-model
```

### 5. Label the data
Next we can use the cluster centroids to label the raw data. The labeled data set will be used by the app to generate recommendations.
```shell
make label
```

### 6. Model Evaluation
We can also evaluate the model before deployment using user-defined metrics (can be configured in `config/config_modeling.yml`)
```shell
make evaluate
```

## Load Data Into Database

### Create the database 
```bash
make create-db
```

#### Ingest Data Into Database
```shell
make ingest
```

## Running the app
Once the labeled data has been loaded in to the data set specified by `SQLALCHEMY_DATABASE_URI`, we can simply use the following make command to deploy the webapp.
```shell
make webapp
```

#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill final-project-app
```

## Testing

To run the tests, run: 

```bash
docker run final-project-tests
```
