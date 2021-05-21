import logging.config
import sys

import pymysql.err
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger(__name__)

base = declarative_base()


class User(base):
    """Create a data model for the database to be set up for capturing users"""
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    steam_id = Column(String(25), unique=True, nullable=False)

    def __repr__(self):
        return "<Users(id='%r', steam_id='%r')>" % (self.id, self.steam_id)


class Games(base):
    """Create a data model for the database to be set up for capturing games"""
    __tablename__ = 'Games'
    id = Column(Integer, primary_key=True)
    game_id = Column(String(25), unique=True, nullable=False)
    game_title = Column(String(100), unique=False, nullable=False)

    def __repr__(self):
        return "<Games(id='%r', game_id='%r', game_title='%r')>" % (self.id, self.game_id, self.game_title)


class OwnedGames(base):
    """Create a data model for the database to be set up for capturing how long a user has played a game"""
    __tablename__ = 'OwnedGames'
    id = Column(Integer, primary_key=True)
    steam_id = Column(String(25), unique=False, nullable=False)
    game_id = Column(String(100), unique=False, nullable=False)
    hours_played = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return "<OwnedGames(id='%r', steam_id = '%r', game_id='%r', hours_played='%r')>" % (self.id, self.steam_id,
                                                                                            self.game_id,
                                                                                            self.hours_played)


def create_db(engine_string):
    """Creates a database at the specified engine_string that contains the data models inherited by `Base`. This
        function does not return anything, instead it creates a database instance at the specified location that
        contains the Games, Players, and OwnedGames tables.
    Args:
        engine_string: :obj:`String` String defining the connection to the SQL database
    Returns:
        None
    """

    # Create db at specified engine string
    try:
        logger.info("Starting database initialization")
        engine = sqlalchemy.create_engine(engine_string)
        base.metadata.create_all(engine)
        logger.info("Tables have been created at %s", engine_string)

    except pymysql.err.OperationalError as e:
        logger.error(e, "Could not connect to the mysql server. Make sure you are on the Northwestern VPN before "
                        "retrying")
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)
