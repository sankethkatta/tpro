import twitter
import csv
import string
import sys
from topusers import users
import os
# This script gets all public tweets(including retweets) of a user.
# To run this: python tweetscraper.py <username>
# You will find a csv with a tokenized list of tweets in username.csv
api = twitter.Api(consumer_key = '723w730Htbdk4pgyb2sdEA',
                   consumer_secret='wk6CoLNX2SxxZNWvlnaDYocmp6AUtQqTUVzGC1eKlEg',
                   access_token_key = '20957704-icOHaCW6yqxJmUSamU9qMZI7t9kirpMYWKC9Ck0o',
                   access_token_secret = '4a1IA9Y0mRZs6a5CHmsFtyNw4T37xc9rgHv1Tht2UbM')

total = 0
for i in xrange(len(users)):
    print "User: %s, Index: %d" % (users[i], i)
    data = []
    max_id=None
    while True:
        statuses = api.GetUserTimeline(users[i], count = 200, max_id = max_id, include_rts = True)
        total = total + len(statuses)
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
