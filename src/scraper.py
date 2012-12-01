#!/usr/bin/env python
import tweepy
from tweepy import Cursor
import getpass
import sys
import time
from collections import defaultdict, deque
import re
import pprint
import sqlite3
import argparse
import json
import nltk
import nltk.corpus as corpus
import random

# attempt to load secret keys from json file
# in our repo, we will not have this actual file
# so it will except, and basically return a dict
# with only string values
try:
  obj = json.loads(open('auth.json').read())
except:
  obj = defaultdict(str)

# try to read the dictionary, if the file was there, then it read the
# actual keys. Otherwise, it'll just be empty strings
consumer_key = obj['consumer_key']
consumer_secret = obj['consumer_secret']
access_token = obj['access_token']
access_token_secret = obj['access_token_secret']

auth = [consumer_key, consumer_secret, access_token, access_token_secret]
stopwords = set(corpus.stopwords.words('english'))

class TwitterApplication(object):
  """
  Wrapper class for creating a twitter application

  Takes care of authentication in the constructor, but you must provide
  the keys right away. There is no option of delaying authentication
  """
  
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self, consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret):

    """
    Constructs the oauth variables based on the inputs to the constructor
    """
    self._consumer_key = consumer_key
    self._consumer_secret = consumer_secret
    self._access_token = access_token
    self._access_token_secret = access_token_secret

    self._auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    self._auth.set_access_token(access_token, access_token_secret)

    self._api = tweepy.API(self._auth)

  @property
  def auth(self):
    return self._auth

  @property
  def api(self):
    """
    Returns a reference to the tweepy.API so that you can call all
    of the wonderful methods from the api

    example:
      app = TwitterApplication(consumer_key,consumer_secret,access_token,access_token_secret)
      app.api.update_status("new status!")
    """
    return self._api

  def tokenize(self, s):
    return [w for w in re.findall('\w+', s) if w not in stopwords]

class TwitterScraper(TwitterApplication):
  
  def __init__(self, **kwargs):
    TwitterApplication.__init__(self, **kwargs)
    self.users_to_scrape = deque(kwargs.get('users_to_scrape', ['justinbieber', 'obama']))

  def scrape(self, username='barackobama'):
    with open('%s.csv' % username, 'wb') as f:

        for status in Cursor(self.api.user_timeline, id=username, count=10000).items():
          val = ('{username},{status}\n'.format(username=username, status=status.text.encode('ascii', 'ignore')))
          f.write(val)
          time.sleep(random.random()*3)


      
if __name__ == '__main__':
  app = TwitterScraper()
  try:
      app.scrape(sys.argv[1])
  except:
      app.scrape()    





