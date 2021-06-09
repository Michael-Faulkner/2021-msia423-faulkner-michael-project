# MSiA423 Template Repository

Michael Faulkner

QA: Brian Lewis

<!-- toc -->

- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

<!-- tocstop -->

# Project Charter

## Vision
In 2020 the amount spent on video games was $56.9 billion which was a 27% increase from 2019. Steam was one of the platforms that gained from this increase as it is one of the most popular places people go to find and buy new games. With such a large increase in the amount spent on video games last year, it's no surprise that Steam broke the record for most concurrent users on a video game platform 6 times, with the last one being at over 26 million concurrent active users. One advantage that Steam has over other platforms is that they offer over 30,000 different video games that users are able to purchase and download without having to leave their home. With such a large catalog of different games, users can be overwhelmed and abandon their search when they are trying to find a new game to play. 

My vision is to create more accurate and personalized recommendations to increase user engagement and satisfaction with the Steam platform.

## Mission

To achieve the above vision, a recommender system utilizing collaborative-based filtering will be created. The model will take a user's (user A) most played games and find a group of users who also own those games. Then the model will find the most popular games among the group of new users and return an ordered list of recommended games to user A. 

Data containing the video games purchased by 69,277 unique users have been previously collected and will be used for the collaborative filtering recommender system. [Steam User and Item Data](https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data) 

## Success Criteria

Model Performance Metric:

   1. The Recommender System will be deployed if an AUC score of at least 0.75 is achieved.

Business Metrics:

   1. Use an A/B test to see if the recommender systems leads to an increase in customers buying more games and spending more time on Steam
   2. Compare the average review left by users who were recommended a game versus discovering it on their own
    

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── setup.sh                      <- Start up script for setting up database and downloading raw data.
│   ├── Dockerfile_Setup              <- Dockerfile for building image to run setup
│   ├── Dockerfile_Pipeline           <- Dockerfile for building image to run model pipeline
│   ├── Dockerfile_App                <- Dockerfile for building image to run app
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API
│   ├── config.yaml                   <- Configurations setup and model pipeline
│
├── data                              <- Folder that contains data used or generated. 
│   ├── raw/                          <- Raw data sources, downloaded from the internet or S3
│   ├── processed/                    <- Processed raw data sources
│   ├── results/                      <- Model results
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
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
├── src/                              <- Source data for the project
│   ├── create_db.py                  <- Script to create database and tables
│   ├── get_data.py                   <- Script to download data from website. Also includes downloading to/from S3
│   ├── ingest_data.py                <- Script to put data into the database
│   ├── model.py                      <- Script to build the LightFM model
│   ├── process_data.py               <- Script to process raw data
│
├── test/                             <- Files necessary for running model tests (see documentation below)
│   ├── outputs/                      <- outputs from tests
│   ├── test_cosine_similarity_matrix <- Unit tests for cosine similarity matrix
│   ├── test_create_games_csv         <- Unit tests for create games csv
│   ├── test_create_interaction_matrix<- Unit tests for create interaction matrix
│   ├── test_create_user_games_csv    <- Unit tests for create user games csv
│   ├── test_make_sparse              <- Unit tests for make sparse
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies
├── Makefile                          <- Command line shortcuts to run docker commands

```


## Building Docker Images


There are three dockerfiles used for this webapp, one handles the data acquisition, another handles the model pipeline, and the final one is responsible for launching the webapp. If starting from scratch all three must be built and ran in order for the app to work. If you have access to my S3 bucket, starting with any of the Docker commands will work as the program will downloaded the needed files from S3. 


### Data Acquisition Docker Image

This Dockerfile is used for data acquisition, uploading to s3, and creating the database/tables at the specified address.

#### Makefile:
```bash
make setup
```
#### Docker:
```bash
docker build -f app/Dockerfile_Setup -t setup .
```


### Model Pipeline Docker Image

This Dockerfile is responsible for running the model pipeline, data ingestion, and unit testing.

#### Makefile:
```bash
make pipeline
```
#### Docker:
```bash
docker build -f app/Dockerfile_Pipeline -t pipeline .
```

### Webapp Docker Image

This Dockerfile is used for launching and maintaining the webapp.

#### Makefile:
```bash
make app
```
#### Docker:
```bash
docker build -f app/Dockerfile_App -t webapp .
```

## Environmental Setup

Before creating any Docker commands the following enviromental variables should be exported to your current terminal/command line environment.

The AWS keys are used to access the S3 bucket which is need for the data acquisition, model pipeline, and webapp portion of the project.

```bash
export AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key> 
````

The ```SQLALCHEMY_DATABASE_URI``` is an optional argument that creates the connection between the python script and the database. It should be of the form ```{dialect}://{user}:{pw}@{host}:{port}/{db}```. If no ```SQLALCHEMY_DATABASE_URI``` is specified the database will be created locally at ```sqlite:///data/msia423_db.db``` and you can ignore any mentions of requiring ```SQLALCHEMY_DATABASE_URI``` in the following commands.

```bash
export SQLALCHEMY_DATABASE_URI="DATABASE_ENGINE_STRING"
```


## Data Acquistion

These commands will make a request to the target url containing the Steam game and Steam user data. The data will be downloaded, unzipped, and parsed into a JSON format. The two JSON files will then be uploaded to the S3 bucket specified in the ```config.yaml``` file. Both the AWS crednetials and ```SQLALCHEMY_DATABASE_URI``` are needed for this step.


#### Makefile:
```bash
make raw
```
#### Docker:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI --mount type=bind,source=$(pwd),target=/app/ setup
```

## Model Pipeline

There are three choices when it comes to running portions of the model pipeline: data procesing, model building, and the entire pipeline. 

### Full Pipeline
The easiest way to run the pipeline is to do the whole thing in one go. Either of these commands will accomplish that. If the ```pipeline_with_ingest``` in the ```config.yaml``` file is set to ```True```, both the AWS crednetials and ```SQLALCHEMY_DATABASE_URI``` are needed. However, by default this is set to ```False```, and only the AWS credentials need to be provided for this step.

#### Makefile:
```bash
make full
```
#### Docker:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI--mount type=bind,source=$(pwd),target=/app/ pipeline run.py full --config=conf
```

### Data Processing

If only processing the raw data to csv file is desired, these commands can be run to only run the data processing steps. To download the raw data from the S3 bucket, AWS credentials are needed.

#### Makefile:
```bash
make process
```
#### Docker:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source=$(pwd),target=/app/ pipeline run.py process_data --config=config/config.yaml
```

### Model Building

Once the data has been processed, the model can be built using these commands. Since the results are saved to S3 for the webapp to use, AWS credentials are needed. 

#### Makefile:
```bash
make model
```
#### Docker:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source=$(pwd),target=/app/ pipeline run.py model --config=config/config.yaml
```

### Ingesting Data

If the user decides not to ingest data automatically during the pipeline due to the amount of time data ingestion can take (30+ mins), data ingestion can be conducted using the following commands. The data needs to be saved from the data processing stages so the script can open it and start populating the databse. Only the ```SQLALCHEMY_DATABASE_URI``` needs to be specified for this step.

#### Makefile:
```bash
make ingest
```
#### Docker:
```bash
docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source=$(pwd),target=/app/ pipeline run.py ingest --config=config/config.yaml
```

### Unit Tests
Tests exist to make sure the data processing steps are performing correctly. To run them either of the following commands will work.

#### Makefile:
```bash
make tests
```
#### Docker:
```bash
docker run pipeline -m pytest
```

## Web App

To launch the web app, either of the commands will work. Please note that the files uploaded to S3 during the model pipeline are required for the web app to launch. Since access to S3 and the database are needed for this process, both the AWS credentials and ```SQLALCHEMY_DATABASE_URI``` should be sourced.

#### Makefile:
```bash
make flask
```
#### Docker:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI -p 5000:5000 --mount type=bind,source=$(pwd),target=/app/ webapp
```

## Other Useful Tips

### Clean-up
Since intermediate files are created during the different model pipeline steps, this clean up command clears the raw, processed, and results file. In addition it cleans up artifacts produced by one of the tests. 

#### Makefile:
```bash
make clean
```
#### Docker:
```bash
	rm data/raw/*
	rm data/processed/*
	rm data/results/*
	rm tests/outputs/*
```

### Model Reproducibility

There is one variable in the config.yaml file that should be noted if model reproducibility is a top priority. The first is the ```n_jobs``` variable as this controls the number of cores used during model training. In order for the model to be perfectly reproduicble, ```n_jobs``` needs to be set to ```1```. This will make the model take significantly longer to train, but the results will be the same each time the pipeline is run.

### Memory

Due to the small memory limit on my personal laptop, generator functions were used throughout the project to keep the memory use low. In spite of this, Docker needs to have at least 5 GB of free memory in order to successfully get through all portions of the model pipeline. If you are running the pipeline and getting Code 137 from Docker, this memory limit might need to be increased. 
