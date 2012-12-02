import twitter
import csv
import string
import sys
from topusers import users
import os
# This script gets all public tweets(including retweets) of a user.
# To run this: python tweetscraper.py <username>
# You will find a csv with a tokenized list of tweets in username.csv
api = twitter.Api(consumer_key = '7i7MFfbiHCP4E7i1l9S2g',
                   consumer_secret='jGwDVgkdFu7GZIntPnyBq7wSgtTurtlYwvXAfRbxCPY',
                   access_token_key = '15202847-lOjmNyFbxjImFOESPjGDue7mVgYuy9868Aghzurw',
                   access_token_secret = 'XK0wDtdYfTW77bKv8RuQD1lqXuVpilaYCoEZ3YohUA')

users = [username.lower() for username in users]
for i in xrange(80, 500):
    print "User: %s, Index: %d" % (users[i], i)
    data = []
    max_id=None
    while True:
        statuses = api.GetUserTimeline(users[i], count = 200, max_id = max_id, include_rts = True)
        for s in statuses:
            data.append(s)
            max_id = s.id
        if len(statuses) == 0:
            break
        max_id = max_id - 1

    #writes to a csv
    csvFileName = os.path.join('topuserstweets2', users[i] + ".csv")
    count = 0
    with open(csvFileName, 'wb') as f:
        writer = csv.writer(f)
        for status in data:
            count = count + 1
            statusText = status.text.encode('ascii', 'ignore')
            writer.writerow([users[i], statusText])
