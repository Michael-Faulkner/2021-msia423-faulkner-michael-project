import logging.config
import sys

import pymysql.err
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

base = declarative_base()


class Games(base):
    """Create a data model for the database to be set up for capturing games"""
    __tablename__ = 'Games'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, unique=False)
    title = Column(String(100), unique=False)
    genre = Column(String(100), unique=False)
    release_date = Column(String(100), unique=False)
    url = Column(String(100), unique=False)

    def __repr__(self):
        return "<Games(id='%r', game_id='%r', game_title='%r')>" % (self.id, self.game_id, self.title)


def create_db(engine_string, remove_old):
    """Creates a database at the specified engine_string that contains the data models inherited by `Base`. This
        function does not return anything, instead it creates a database instance at the specified location that
        contains the Games, Players, and OwnedGames tables.
    Args:
        engine_string: :obj:`String` Defines the connection to the SQL database
        remove_old: :obj:`Boolean` Specifies whether the old table should be deleted to avoid adding duplicates
    Returns:
        None
    """

    try:

        logger.info("Starting database initialization")
        engine = sqlalchemy.create_engine(engine_string)
        if remove_old:
            base.metadata.drop_all(engine)
        base.metadata.create_all(engine)
        logger.info("Tables have been created at %s", engine_string)

    except pymysql.err.OperationalError as e:
        logger.error(e, "Could not connect to the mysql server. Make sure you are on the Northwestern VPN before "
                        "retrying")
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)


class GameManager:
    """Manager for database session that allows the addition of new games to the database"""

    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string pointing to the local or RDS database
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes database session
        Returns: None
        """
        self.session.close()

    def add_game(self, game_id: int, title: str, genre: str, release_date: str, url: str) -> None:
        """Adds additional games to the Games table.
        Args:
            game_id :obj:`int` ID given to the game by Steam
            title :obj:`String` Title of the game
            genre :obj:`String` Genres that the game belong to
            release_date :obj:`String` Date the game was released on
            url :obj:`String` URL that points to the Steam Store page
        Returns:None
        """

        session = self.session
        game = Games(game_id=int(game_id), title=title, genre=genre, release_date=release_date, url=url)
        session.add(game)
        session.commit()
