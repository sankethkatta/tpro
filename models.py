from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from views import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tpro.db'
db = SQLAlchemy(app)

class BaseModel(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)

    def save(self):
        """ One-hit commit function """
        db.session.add(self)
        db.session.commit()

class Term(BaseModel):

    __tablename__ = 'terms'
    term = db.Column(db.String(80), unique=True)

    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return 'Term(%r)' % self.term
        

class User(BaseModel):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return 'User(%r)' % self.username
