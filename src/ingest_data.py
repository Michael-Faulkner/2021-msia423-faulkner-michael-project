import logging
import sys

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from src.create_db import create_db, GameManager

logger = logging.getLogger(__name__)


def ingest_data(engine_string, remove_old, games_csv_filepath, game_id_column, game_name_column, release_date_column,
                url_column, genres_column):
    """
    Puts the game information dataframe into the sql database.
    Args:
        engine_string: obj:`String` Defines the connection to the SQL database
        remove_old: obj:`Boolean` Specifies whether the old table should be deleted to avoid adding duplicates
        games_csv_filepath: obj:`String` filepath to the csv file containing the Steam game information
        game_id_column: obj:`String`  column name where the game id is stored
        game_name_column: obj:`String` column name where the game name is stored
        release_date_column: obj:`String` column name where the release date is stored
        url_column: obj:`String` column name where the url is stored
        genres_column: obj:`String` column name where the genre is stored
    Returns:
        None
    """
    if remove_old:
        logger.info("Removing old database at %s", engine_string)
        create_db(engine_string, remove_old)
    games = pd.read_csv(games_csv_filepath)
    games = games.fillna(' ')
    gm = GameManager(engine_string=engine_string)
    ids = games[game_id_column].tolist()
    app_names = games[game_name_column].tolist()
    release_dates = games[release_date_column].tolist()
    urls = games[url_column].tolist()
    genres = games[genres_column].tolist()
    logger.info("Ingesting data into database located at %s", engine_string)
    try:
        for i in range(len(games)):
            gm.add_game(int(ids[i]), app_names[i], genres[i], release_dates[i], urls[i])
        gm.close()
        logger.info("Added %d games to the database", len(games))

    except SQLAlchemyError as e:
        logger.error("There was an error while adding games to the database: %s", e)
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)
