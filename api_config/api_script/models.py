from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from .config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    bluesky_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True, index=True)
    bluesky_id = Column(String, unique=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    language = Column(String)
    posted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("Author")
    user = relationship("User")

class Detection(Base):
    __tablename__ = 'detection'
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    label = Column(String)
    probability = Column(Float)
    model_used = Column(String)
    threshold = Column(Float)
    verified = Column(Boolean)
    verified_source = Column(String)
    detection_date = Column(DateTime, default=datetime.utcnow)

    tweet = relationship("Tweet")

class Sentiment(Base):
    __tablename__ = 'sentiment'
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    label = Column(String)
    scores = Column(Text)  # JSON stocké sous forme de chaîne
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    tweet = relationship("Tweet")

def init_db():
    Base.metadata.create_all(bind=engine)
