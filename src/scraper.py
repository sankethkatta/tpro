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
    return re.findall('\w+', s)

class TwitterScraper(TwitterApplication):
  
  def __init__(self, **kwargs):
    TwitterApplication.__init__(self, **kwargs)
    self.users_to_scrape = deque(kwargs.get('users_to_scrape', ['justinbieber']))

  def scrape(self):
    with open('scraper_data.csv', 'w') as f:

      while True:
        # pop the first user off the stack
        username = self.users_to_scrape.pop()
        # push them to the end of the stack
        self.users_to_scrape.appendleft(username)

        for status in Cursor(self.api.user_timeline, id=username, count=1000).items():
          print status.text
          for w in self.tokenize(status.text):
            val = ('{username},{w}\n'.format(username=username, w=w))
            f.write(val)

      
if __name__ == '__main__':
  app = TwitterScraper()
  app.scrape()





