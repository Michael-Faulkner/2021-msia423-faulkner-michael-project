import logging
import pandas as pd
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
import sqlalchemy


def createTable():
    conn_type = "mysql+pymysql"
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    host = os.environ.get("MYSQL_HOST")
    port = os.environ.get("MYSQL_PORT")
    database = os.environ.get("DATABASE_NAME")
    engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)

    Base = declarative_base(engine_string)

    class User(Base):
        """Create a data model for the database to be set up for capturing songs """
        __tablename__ = 'Users'
        id = Column(Integer, primary_key=True)
        steam_id = Column(String(25), unique=True, nullable=False)

        def __repr__(self):
            return '<steam_id %r>' % self.steam_id

    class Games(Base):
        """Create a data model for the database to be set up for capturing songs """
        __tablename__ = 'Games'
        id = Column(Integer, primary_key=True)
        game_id = Column(String(25), unique=True, nullable=False)
        game_title = Column(String(100), unique=False, nullable=False)

        def __repr__(self):
            return '<game %r>' % self.game_title

    class OwnedGames(Base):
        """Create a data model for the database to be set up for capturing songs """
        __tablename__ = 'OwnedGames'
        id = Column(Integer, primary_key=True)
        steam_id = Column(String(25), unique=False, nullable=False)
        game_id = Column(String(100), unique=False, nullable=False)

    # set up sqlite connection

    engine = sqlalchemy.create_engine(engine_string)
    # create the tracks table
    Base.metadata.create_all(engine)


createTable()
