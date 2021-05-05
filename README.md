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
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
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
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Building the Docker image



The Dockerfile used for data acquisition, uploading to s3, and creating the database is found in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t steamRecommender .
```

This command builds the Docker image, with the tag `steamRecommender`, based on the instructions in `app/Dockerfile` and the files existing in this directory.

### Acquire the data
The data can be downloaded by running the command below once the Docker image has been built. It can also be found at http://deepx.ucsd.edu/public/jmcauley/steam/australian_users_items.json.gz.

```bash
docker run steamRecommender run.py get_data --upload=False
```
get_data can also take the following optional arguments:

```bash
gzip_file_path: Where the downloaded data file is stored locally.
url: The target url where the data is.
upload: Whether the data will be automatically uploaded to S3
```
To utilize the optional arguments stated above, a command similar to the one below can be run.

```bash
docker run steamRecommender run.py get_data upload=False --gzip_file_path FilePath.gz --url www.website.com/data.gz
```

The get_data input can also upload the downlaoded gzip file to S3 by setting the upload argument to True. In order for the data to be successfully uploaded to S3 both the aws_access_key_id, and aws_secret_access_key variables have to be supplied in the Docker command as environment variables. 
```bash
export AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key> 
````
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY msia423 run.py get_data
```

In addition to the optional arguments found above, when using upload=True there are two more additional arguments.

```bash
bucket_name: The name of the target bucket on S3
bucket_path: The path where the data file will be stored on S3. 
```
 
The files should be downloaded, and stored in the `data/raw` folder.


### Initialize the database 

To create the database on RDS, five environmental variables need to be supplied to Docker. To set these variables in your environment, open your terminal and run these commands.
```bash
export MYSQL_USER="YOUR_USERNAME"
export MYSQL_PASSWORD="YOUR_PASSWORD"
export MYSQL_HOST="localhost"
export MYSQL_PORT="3306"
export DATABASE_NAME="YOUR_DATABASE_NAME"
```

Once the five variables above have been set, they can be passed into the Docker image with the create_db command to create the database as shown below.

```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME steamRecommender run.py create_db
```

There are two alternative options to create the database. The first is to specify the engine_string argument that defines where the database should be created.
```bash
docker run steamRecommender run.py create_db --engine_string=<database path>
```

The final option is to not include any environmental variables, or an engine string, and the create_db function will create the database locally at:
```bash
sqlite:///data/msia423_db.db
```


 
