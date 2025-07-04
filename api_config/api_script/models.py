# api_config/api_script/models.py

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
# Assurez-vous que cet import fonctionne avec votre structure
from .config import DATABASE_URL
from flask_login import UserMixin

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def check_password(self, password):
        # Assurez-vous d'utiliser une vraie vérification de hash ici
        return self.password_hash == password

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    bluesky_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Cette relation permet de faire author.tweets
    tweets = relationship("Tweet", back_populates="author")

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

    author = relationship("Author", back_populates="tweets")
    user = relationship("User")

    # ==================== EXPLICATION DE LA MODIFICATION ====================
    # La ligne ci-dessous est la seule modification à apporter.
    # Elle crée un "pont" entre un Tweet et ses Détections.
    # - `relationship("Detection", ...)`: Indique que la classe Tweet est liée à la classe Detection.
    # - `back_populates="tweet"`: Crée le lien inverse (pour pouvoir faire detection.tweet).
    # - `cascade="..."`: Assure que si un Tweet est supprimé, toutes ses détections associées le sont aussi.
    # Grâce à cette ligne, votre template pourra accéder à la liste des détections
    # d'un tweet en utilisant simplement `tweet.detections`.
    # ========================================================================
    detections = relationship("Detection", back_populates="tweet", cascade="all, delete-orphan")


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

    # On s'assure que la relation inverse est bien définie.
    tweet = relationship("Tweet", back_populates="detections")


# Le reste de vos modèles (Sentiment, etc.) et fonctions (init_db) ne change pas.
class Sentiment(Base):
    __tablename__ = 'sentiment'
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    label = Column(String)
    scores = Column(Text)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    tweet = relationship("Tweet")

def init_db():
    Base.metadata.create_all(bind=engine)
