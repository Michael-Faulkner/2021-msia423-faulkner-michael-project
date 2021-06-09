import traceback
import logging.config

import pandas as pd
from flask import Flask
from flask import render_template, request

# Initialize the Flask application
from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.get_data import download_s3
from src.create_db import Games, GameManager

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session


download_s3(app.config['LOCAL_SIMILARITY_PATH'], app.config['BUCKET_NAME'], app.config['BUCKET_SIMILARITY_PATH'])
download_s3(app.config['LOCAL_GAMES_PATH'], app.config['BUCKET_NAME'], app.config['BUCKET_GAMES_PATH'])
game_manager = GameManager(app, engine_string=SQLALCHEMY_DATABASE_URI)
similarities = pd.read_csv(app.config['LOCAL_SIMILARITY_PATH'])
similarities = similarities.rename(columns={'Unnamed: 0': app.config['GAME_COLUMN']})
game_df = pd.read_csv(app.config['LOCAL_GAMES_PATH'])


@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """

    try:
        games = game_manager.session.query(Games).order_by(Games.game_id).limit(app.config['MAX_ROWS_SHOW']).all()
        logger.debug("Index page accessed")
        return render_template('index.html', games=games)

    except Exception:
        traceback.print_exc()
        logger.warning("Not able to display games, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def show_cluster_or_id():
    """View that process a POST with input from user.
    User can input game_id, game_name, or cluster_Id.
    In each case, the Guru will retur the top 10 games in the cluster related to the entity specified by the user input.
    :return: redirect to index page
    """
    # If game_id is provided => find the cluster for that game and return top 10 games by user rating in that cluster
    if request.form.get('game_id'):
        try:
            results = list(similarities[[app.config['GAME_COLUMN'], str(request.form['game_id'])]].sort_values(
                str(request.form['game_id']), ascending=False)[app.config['GAME_COLUMN']].iloc[1:app.config['MAX_RECOMMENDATIONS']+1])
            games = game_manager.session.query(Games).filter(Games.game_id.in_(results)).limit(
                app.config['MAX_RECOMMENDATIONS']).all()
            logger.debug("Returning %d games", app.config['MAX_RECOMMENDATIONS'])
            return render_template('index.html', games=games)
        except Exception:
            traceback.print_exc()
            logger.warning("Not able to display games, error page returned")
            return render_template('error.html')

    else:
        try:
            game_id = int(
                list(game_df[game_df['app_name'] == request.form.get('game_name')][app.config['GAME_COLUMN']])[
                    0])

            results = list(
                similarities[[app.config['GAME_COLUMN'], str(game_id)]].sort_values(str(game_id), ascending=False)[
                    app.config['GAME_COLUMN']].iloc[1:app.config['MAX_RECOMMENDATIONS']+1])
            games = game_manager.session.query(Games).filter(Games.game_id.in_(results)).limit(
                app.config['MAX_RECOMMENDATIONS']).all()
            logger.debug("Returning %d games", app.config['MAX_RECOMMENDATIONS'])
            return render_template('index.html', games=games)
        except Exception:
            traceback.print_exc()
            logger.warning("Not able to display games, error page returned")
            return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
