import os
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "steam-recommender"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 50
MAX_RECOMMENDATIONS = 25
GAME_COLUMN = 'id'
BUCKET_SIMILARITY_PATH = 'results/similarities.csv'
LOCAL_SIMILARITY_PATH = 'data/results/similarities.csv'
BUCKET_GAMES_PATH = 'processed/steam_games.csv'
LOCAL_GAMES_PATH = 'data/processed/steam_games.csv'
BUCKET_NAME = '2021-msia423-faulkner-michael'

# Connection string
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('DATABASE_NAME')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/msia423_db.db'
else:
    SQLALCHEMY_DATABASE_URI = '{dialect}://{user}:{pw}@{host}:{port}/{db}'.format(dialect=DB_DIALECT, user=DB_USER,
                                                                                  pw=DB_PW, host=DB_HOST, port=DB_PORT,
                                                                                  db=DATABASE)
