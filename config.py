# config.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:informatica1934@localhost/Terian_BD'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG = True

