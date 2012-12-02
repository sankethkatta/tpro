from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from views import app
from stemming.porter import stem as stemmer
import csv
from nltk.corpus import stopwords
import re
from search_engine import Vector
from sqlalchemy.sql import func

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tpro.db'
db = SQLAlchemy(app)

STOPWORDS = set(stopwords.words())
STOPWORDS.add("http")
STOPWORDS.add("com")

INDUSTRIES = dict(
    politics=["whitehouse", "KarlRove", "SenJohnMcCain", "nprpolitics", 
              "SpeakerBoehner", "chavezcadanga", "thehill", "johnboehner", 
              "GStephanopoulos", "JimDeMint", 'HHShkMohd', 
              'BarackObama', 'QueenRania', 'ShashiTharoor', 'KRuddMP', 'CoryBooker'
    ],

    sports=["espn", "KingJames", "mcuban", "DwyaneWade", "WojYahooNBA",
            "SInow", "drewbrees", "MichelleDBeadle", "darrenrovell", 
            "JayGlazer"
    ],
    entertainment=["Sony Pictures", "Universal Pictures", "LIONSGATE MOVIES",
            "Michael Keck", "Miramax", "foxsearchlight", "Yahoo! Movies",
            "Peter Sciretta", "Hollywood Reporter", "Helen O'Hara"
    ],
    health=["Health Magazine", "NYTimes Health", "NBC News Health", 
            "CBS News Health", "CDC_eHealth"
    ],
    music=["ladygaga", "pitchforkmedia", "questlove", "coldplay", "GreenDay", "thekillers", "RollingStone", "Ludacris", "Eminem",
    "rihanna", "justinbieber", "katyperry", "jason_mraz", "kanyewest"], 

    food=["Foodimentary", "Rick_Bayless", "TylerFlorence", "FoodNetwork", 
        "seriouseats", "LATimesfood", "steamykitchen", 'ChefChiarello', 
        'ruthreichl', 'NoReservations'],
    technology=[
        "ForbesTech", "anildash", "RWW", "chadfowler", "TechCrunch", "cultofmac", "SteveCase",
        "biz", "kevinrose", "twitter", "gadgetlab", "google", "facebook", 
        "davemorin", "Padmasree", "bgurley"
    ],
    funny=[
        "CollegeTownLife", "RayWJ", "BillCosby", "EugeneMirman", "Jenna_Marbles",
        "cracked", "TheAwkwardTweet", "charliesheen", "ActuallyNPH", "rickygervais",
        "galifianakisz", "louisck", "azizansari", "DannyDeVito"
    ],
    fashion=[
        "VictoriasSecret", "heidiklum", "MrJayManuel", "cmbenz", "Refinery29", "hm",
        "ninagarcia", "TOMS", "bryanboy", "BrooklynDecker", "juneAmbrose", 
        "voguemagazine", "beautylish", "MirandaKerr", "VanityFair", "lululemon",
        "TwitterFashion"
    ],
    family=[
        "momfluential", "thebump", "RealSimple", "ToysRUs", "Todaysparent", 
        "TheBloggess", "singlemommyhood", "supernanny_com", "butterflymoms", 
        "playgrounddad", "ICanGrowPeople", "parentsmagazine", "TheMommyologist",
        "sesamestreet", "DailyParentTip", "parenthacks",
    ],
    business=[
        "ev", "realDonaldTrump", "ramseyshow", "johnolilly", "Reuters_Biz",
        "StephenRCovey", "Forbes", "demandrichard", "anandmahindra", "themotleyfool",
        "JeffBooth", "zappos", "MarketWatch", "garyvee", "FortuneMagazine", 
        "todsacerdoti", "FinancialTimes"
    ],

    science=[
        "sciam", "Astro_Nicole", "drkiki", "digg_sciences", "Astro_Mike", "pzmyers",
        "bengoldacre", "Astro_Soichi", "apod", "NSF", "NASAHurricane", "bbcscitech",
        "NASA", "science", "CERN", "NASAJPL", "smithsonian", "EQTW", "NASAKepler",
    ],
    religion =['onfaith', 'dalailama', 'JoelOsteen', 'yahya_ibrahim', 'DanielLapin', 
    'judahsmith', 'CSLewis', 'DeepakChopra', 
    'JoyceMeyer', 'RabbiYonah', 'EbooPatel', 'KayArthur', 'twitterreligion'],

    philanthropy=['melindagates', 'SomalyMam', 'dosomething', 'hrw', 'SavetheChildren', 
    'Water', 'Kiva', 'changemakers', 'WWF', 'Ashoka', 'Refugees', 'gatesfoundation', 
    'CARE', 'LiteracyBridge', 'rotary', 'LIVESTRONGCEO' ], 

    television = ['DannyDeVito', 'kenjeong', 'sela_ward', 'KaleyCuoco', 'ZooeyDeschanel', 'BRUCKHEIMERJB',
    'DannyZuker', 'WhitneyCummings', 'ericstonestreet', 'evalaruecappoo', 'PhilKeoghan',
    'Y_Strahovski', 'wayansjr', 'THEsaragilbert', 'PatriciaHeaton',
     'kunalnayyar', 'duplaselton', 'GordonRamsay01', 'twittertv', 'bjnovak', 'ZacharyLevi']     

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

    @staticmethod
    def get_vector(industry_id):
        results = db.session.query(Stem.text, func.count(Stem.id)).\
            filter(Stem.id==Term.stem_id, 
                   Term.tweet_id==Tweet.id,
                   Tweet.user_id==User.id, 
                   User.industry_id==industry_id
                   ).group_by(Stem.text)
        return Vector(dict(results))

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

       
class Tweet(BaseModel):

    __tablename__ = 'tweets'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(200), nullable=False)
    

class User(BaseModel):

    __tablename__ = 'users'
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'))
    recommendations = db.Column(db.String(1000))

    def __repr__(self):
        return 'User(%r)' % self.username

   
    @staticmethod
    def get_or_create(username, industry_id=None):
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, industry_id=industry_id).save()
        return user

def tokenize(s):
    return re.findall('\w+', s)

def import_csv_file(industry_name, fname):
    # find the industry in our DB
    industry = Industry.get_or_create(industry_name)
    assert industry is not None, "something bad happened when creating an industry"
    with open(fname, 'r') as f:
        reader = csv.reader(f)

        for username, tweet_text in reader:
            try:
                user = User.get_or_create(username, industry_id=industry.id)
                tweet = Tweet(user_id=user.id, text=tweet_text).save()
                for token in tokenize(tweet_text.lower()):
                    if token not in STOPWORDS:
                        stem = Stem.get_or_create(stemmer(token)) 
                        Term(tweet_id=tweet.id, text=token).save()
            except Exception as err:
                print err

if __name__ == '__main__':
    for industry, users in INDUSTRIES.iteritems():
        for username in users:
            try:
                import_csv_file(industry, '%s.csv' % username.lower())
            except Exception as err:
                pass

