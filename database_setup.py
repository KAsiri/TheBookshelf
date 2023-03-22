import os
from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)

class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self) -> dict:

        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }


class Book(Base):
    __tablename__ = 'book'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(300))
    author_name = Column(String(20))
    publish_year = Column(String(8))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self) -> dict:

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'author_name': self.author_name,
            'publish_year': self.publish_year,
            'user_id': self.user_id,
        }


def create_engine_and_session() -> tuple:
    """
    Creates the database engine and session objects.

    Returns:
    engine (sqlalchemy.engine.base.Engine): The database engine object.
    session (sqlalchemy.orm.session.Session): The database session object.
    """
    db_uri = os.environ.get('DATABASE_URI')
    engine = create_engine(db_uri)
    session = Session(bind=engine)
    return engine, session


def create_database() -> None:
    """
    Creates the database schema.
    """
    engine, _ = create_engine_and_session()
    Base.metadata.create_all(engine)
