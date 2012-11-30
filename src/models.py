from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from views import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tpro.db'
db = SQLAlchemy(app)

class BaseModel(db.Model):
   
    # every model inherits from BaseModel, so they all have an ID
    id = db.Column(db.Integer, primary_key=True)
    __abstract__ = True

    def save(self):
        """ One-hit commit function """
        db.session.add(self)
        db.session.commit()

class Industry(BaseModel):

    __tablename__ = 'industries'
    name = db.Column(db.String(80), unique=True)

class Stem(BaseModel):

    __tablename__ = 'stems'
    text = db.Column(db.String(80), unique=True)

class Term(BaseModel):

    __tablename__ = 'terms'
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    stem_id = db.Column(db.Integer, db.ForeignKey('stems.id'))
    text = db.Column(db.String(80), unique=True)

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Term(%r)' % self.text
       
class Tweet(BaseModel):

    __tablename__ = 'tweets'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(200), nullable=False)
    

class User(BaseModel):

    __tablename__ = 'users'
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'))

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return 'User(%r)' % self.username
