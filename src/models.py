from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from views import app
from stemming.porter import stem as stemmer
import csv

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tpro.db'
db = SQLAlchemy(app)


INDUSTRIES = dict(
    politics=["whitehouse", "KarlRove", "SenJohnMcCain", "nprpolitics", 
              "SpeakerBoehner", "chavezcadanga", "thehill", "johnboehner", 
              "GStephanopoulos", "JimDeMint", 'BarackObama'
    ],

    sports=["espn", "KingJames", "mcuban", "DwyaneWade", "WojYahooNBA",
            "SInow", "drewbrees", "MichelleDBeadle", "darrenrovell", 
            "JayGlazer"
    ],
    movies=["Sony Pictures", "Universal Pictures", "LIONSGATE MOVIES",
            "Michael Keck", "Miramax", "foxsearchlight", "Yahoo! Movies",
            "Peter Sciretta", "Hollywood Reporter", "Helen O'Hara"
    ],
    health=["Health Magazine", "NYTimes Health", "NBC News Health", 
            "CBS News Health", "CDC_eHealth"
    ],

    music=["ladygaga", "pitchforkmedia". "questlove", "coldplay", "GreenDay", "thekillers", "RollingStone", "Ludacris", "Eminem",
    "rihanna", "justinbieber", "katyperry", "jason_mraz", "kanyewest"], 

    food=["Foodimentary", "Rick_Bayless", "TylerFlorence", "FoodNetwork", 
        "seriouseats", "LATimesfood", "steamykitchen", 'ChefChiarello', 
        'ruthreichl', 'NoReservations']
        

)

class BaseModel(db.Model):
   
    # every model inherits from BaseModel, so they all have an ID
    id = db.Column(db.Integer, primary_key=True)
    __abstract__ = True

    def save(self):
        """ One-hit commit function """
        db.session.add(self)
        db.session.commit()
        return self

class Industry(BaseModel):

    __tablename__ = 'industries'
    name = db.Column(db.String(80), unique=True)

    @staticmethod
    def get_or_create(name):
        industry = Industry.query.filter_by(name=name).first()
        if not industry:
            industry = Industry(name=name).save()
        return industry

class Stem(BaseModel):

    __tablename__ = 'stems'
    text = db.Column(db.String(80), unique=True)

    @staticmethod
    def get_or_create(text):
        stem = Stem.query.filter_by(text=text).first()
        if not stem:
            stem = Stem(text=text).save()
        return stem

class Term(BaseModel):

    __tablename__ = 'terms'
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'))
    stem_id = db.Column(db.Integer, db.ForeignKey('stems.id'))
    text = db.Column(db.String(80))


    def __repr__(self):
        return 'Term(%r)' % self.text

    @staticmethod
    def get_or_create(text, tweet_id, stem_id):
        term = Term.query.filter_by(text=text).first()
        if term is None:
            term = Term(tweet_id=tweet_id, stem_id=stem_id, text=text).save()
        return term
       
class Tweet(BaseModel):

    __tablename__ = 'tweets'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(200), nullable=False)
    

class User(BaseModel):

    __tablename__ = 'users'
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'))

    def __repr__(self):
        return 'User(%r)' % self.username

    @staticmethod
    def get_or_create(username, industry_id=None):
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, industry_id=industry_id).save()
        return user

from nltk.tokenize import word_tokenize

def import_csv_file(industry_name, fname):
    # find the industry in our DB
    industry = Industry.get_or_create(industry_name)
    assert industry is not None, "something bad happened when creating an industry"
    with open(fname, 'r') as f:
        for line in f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    username, tweet_text = row
                    user = User.get_or_create(username, industry_id=industry.id)
                    tweet = Tweet(user_id=user.id, text=tweet_text).save()
                    for token in word_tokenize(tweet_text.lower()):
                        stem = Stem.get_or_create(stemmer(token)) 
                        term = Term.get_or_create(token, tweet.id, stem.id)
                except Exception as err:
                    print err

if __name__ == '__main__':
    for industry, users in INDUSTRIES.iteritems():
        for username in users:
            try:
                import_csv_file(industry, '%s.csv' % username)
            except Exception as err:
                print err


