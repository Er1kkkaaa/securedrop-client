import os
import sqlite3
import subprocess

from sqlalchemy import (Boolean, Column, create_engine, DateTime, ForeignKey,
                        Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


# TODO: Store this in config file, see issue #2
DB_PATH = os.path.abspath('svs.sqlite')

engine = create_engine('sqlite:///{}'.format(DB_PATH))
Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)
    journalist_designation = Column(String(255), nullable=False)
    is_flagged = Column(Boolean, default=False)
    public_key = Column(String(10000), nullable=True)
    interaction_count = Column(Integer, default=0, nullable=False)
    is_starred = Column(Boolean, default=False)
    last_updated = Column(DateTime)

    def __init__(self, uuid, journalist_designation):
        self.uuid = uuid
        self.journalist_designation = journalist_designation

    def __repr__(self):
        return '<Source %r>' % (self.journalist_designation)


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)

    # This is whether the submission has been downloaded in the local database.
    is_downloaded = Column(Boolean, default=False)

    # This reflects read status stored on the server.
    is_read = Column(Boolean, default=False)

    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship(
        "Source",
        backref=backref("submissions", order_by=id, cascade="delete")
        )

    def __init__(self, source, uuid, filename):
        self.source_id = source.id
        self.uuid = uuid
        self.filename = filename

    def __repr__(self):
        return '<Submission %r>' % (self.filename)


class Reply(Base):
    __tablename__ = 'replies'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship(
        "Source",
        backref=backref("replies", order_by=id, cascade="delete")
        )

    journalist_id = Column(Integer, ForeignKey('users.id'))
    journalist = relationship(
        "User", backref=backref('replies', order_by=id))

    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)

    def __init__(self, journalist, source, filename, size):
        self.journalist_id = journalist.id
        self.source_id = source.id
        self.filename = filename
        self.size = size

    def __repr__(self):
        return '<Reply %r>' % (self.filename)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<Journalist: {}".format(self.username)
