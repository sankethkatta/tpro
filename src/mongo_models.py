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
    def contains(username):
        match = User.users.find_one({ "username": username })
        return match is not None


    @staticmethod
    def insert(users):
        conditions = { "$or": [{ "username": u['username'] } for u in users] }
        matching_usernames = set(user['username'] for user in User.users.find(conditions))
        users = [user for user in users if user['username'] not in matching_usernames]
        if users:
            print "entering a new user"
            return User.users.insert(users)
        else:
            print "user already exists"

    @staticmethod
    def similar_documents(document, k=10):
        tokens = tokenize(document)
        vector = Vector(document)
        results = sorted([(vector.cosine_similarity(user['features']), user['username']) for user in User.users_containing_terms(tokens)], reverse=True)[:k]
        return results

def tokenize(s):
    return [stem(w) for w in re.findall('\w+', s.lower()) if w not in stopwords]

def import_csv_data():
    data_directory = os.path.realpath(os.path.dirname(__file__)).replace('src', 'scraper/topuserstweets2')
    csv_filenames = [os.path.join(data_directory, fname) \
                     for fname in os.listdir(data_directory)]
    csv_filenames = [fname for fname in csv_filenames if fname.endswith('.csv')]

    idx = 0
    for csv_fname in csv_filenames:
        with open(csv_fname, 'rb') as f:
            reader = csv.reader(f)
            features = Vector()
            user = { 'username': '', 'tweets': []}
            for username, tweet in reader:
                # don't process a csv file if we've already added them to the db
                if User.contains(username):
                    print "already processed %s" % username
                    break
                if not user.get('username'):
                    user['username'] = username
                for token in tokenize(tweet):
                    features[token] += 1
                user['tweets'].append(tweet)
            user['features'] = features
            if user['username'] and user['features'] and user['tweets']:
                User.insert([user])
                idx += 1
                print "username: %s, index: %s" % (username, idx)
if __name__ == '__main__':
    import_csv_data()

       
            

                

    

        








