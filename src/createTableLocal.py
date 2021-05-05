import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData


def createTableLocal(engine_string):
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

    engine = sqlalchemy.create_engine(engine_string)
    Base.metadata.create_all(engine)


createTableLocal('sqlite:///msia423_db.db')
