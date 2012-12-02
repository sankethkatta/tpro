#!/usr/bin/env python
import pymongo
from search_engine import Vector
from stemming.porter import stem
import nltk
import os
import csv
import re
from pprint import pprint

stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords.add('http')
stopwords.add('co')
stopwords.add('com')

connection = pymongo.MongoClient('localhost', 27017)

###########################
##  user = {
##      'username': 'barackobama',
##      'features': { 'change':10, 'we': 30, 'can':90' },
##      'tweets': ['tweet1', 'tweet2', 'tweet3']
##  }
##
###########################
class User(object):
    
    db = connection.tpro
    users = db.users

    @staticmethod
    def get(username):
       user = User.users.find_one({"username": username})
       if user:
           user['features'] = Vector(user.get('features', {}))
       return user
       
    @staticmethod
    def users_containing_terms(terms):
        conditions = {"$or" : [ {'features.%s' % term : {"$gt": 0}} for term in terms]}
        users = list(User.users.find(conditions))
        for user in users:
            user['features'] = Vector(user.get('features', {}))
        return users

    @staticmethod
    def insert(users):
        conditions = { "$or": [{ "username": user['username']} for user in users] }
        matching_usernames = User.users.find(conditions)
        users = [user for user in users if user['username'] not in matching_usernames]
        return User.users.insert(users)

def tokenize(s):
    return [stem(w) for w in re.findall('\w+', s.lower()) if w not in stopwords]

def import_csv_data():
    data_directory = os.path.realpath(os.path.dirname(__file__)).replace('src', 'scraper/topuserstweets2')
    csv_filenames = [os.path.join(data_directory, fname) \
                     for fname in os.listdir(data_directory)]
    csv_filenames = [fname for fname in csv_filenames if fname.endswith('.csv')]

    users = []
    for csv_fname in csv_filenames:
        with open(csv_fname, 'rb') as f:
            reader = csv.reader(f)
            features = Vector()
            user = { 'tweets': []}
            for username, tweet in reader:
                if not user.get('username'):
                    user['username'] = username
                for token in tokenize(tweet):
                    features[token] += 1
                user['tweets'].append(tweet)
            user['features'] = features
            users.append(users)
if __name__ == '__main__':
    import_csv_data()

       
            

                

    

        








