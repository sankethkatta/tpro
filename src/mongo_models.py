#!/usr/bin/env python
import pymongo
from search_engine import Vector
from stemming.porter import stem
import nltk
import os
import csv
import re
from pprint import pprint
from time import time
import scraper
from time import time
from collections import defaultdict
import datetime

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

db = connection.tpro

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
    def all():
        users = list(User.users.find())
        for user in users:
            user['features'] = Vector(user['features'])
        return users

    @staticmethod
    def users_containing_terms(terms):
        START = time()
        #records = db.inverted_index.find({ "$or" : [{ "term": term }  for term in terms]})
        #inverted_index = dict((record["term"], set(record["usernames"])) for \
        #    record in records)
        #usernames = reduce(lambda x, y: x | y, (inverted_index.get(term, set()) for term in terms))
        #users = (u for u in [User.get(uname) for uname in usernames] if u)
        users = (u for u in db.users.find() if u.get("username"))
        results = []
        for user in users:
            user["features"] = Vector(user.get('features', {}))
            results.append(user)
        print "users_containing_terms: %s"  % (time() - START)
        return results

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
    def similar_documents(document, k=20):
       
        recommendation = db.recommendations.find_one({"username": document})
        if recommendation:
            print "found previously cached results"
            created = recommendation.get('created')
            # are the previously found results too old?
            if not created or (datetime.datetime.utcnow()-created).days > 0:
                # delete the outdated recommendation
                db.recommendations.remove("results")
            else:
                results = recommendation.get("results")
                return results[:k]

        user = User.get(document)
        if user:
            # if they are a ground truth user, prove that our results are
            # accurate when analyzing the similarity of their timeline to
            # others in our database
            print "analyzing ground truth"
            vector = user["features"]
        else:
            # a new user has been entered, attempt to scrape their timeline
            print "username entered is neither a ground truth nor has a prior record"
            vector = Vector(scraper.scrape_friends_timelines(document))
            tokens = vector.keys()
        print vector
        users = (u for u in db.users.find() if u.get("features"))
        START = time()

        #pool = mp.Pool(5)
        #results = pool.map(worker, ((vector, user) for user in users))
        #results = sorted(results, reverse=True)
        results = sorted(((vector.cosine_similarity(Vector(user['features'])), user['username']) for user in users), reverse=True)
        if results:
            db.recommendations.insert({"username": document, "results": results, "created": datetime.datetime.utcnow()})
        print "cosine_similarity: %s" % (time() - START)
        return results[:k]

import multiprocessing as mp
def worker(args):
    vector, user = args
    return (vector.cosine_similarity(Vector(user['features'])), user['username'])

def tokenize(s):
    return [stem(w) for w in re.findall('\w+', s.lower()) if w not in stopwords]

def build_mongo_index():
    users = db.users.find()
    inverted_index = defaultdict(set)
    for user in users:
        if not user.get("username"):
            continue
        print user.get("username")
        for token in user.get("features", {}).iterkeys():
            inverted_index[token].add(user["username"])
    records = [{"term":term, "usernames": list(usernames)} for term, usernames in inverted_index.iteritems()]
    for record in records:
        print "inserting record for %s" % record.get("term")
        db.inverted_index.insert(record)
            

        

def import_csv_data():
    data_directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'scraper/topuserstweets2')
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
