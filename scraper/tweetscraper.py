import twitter
import csv
import string
import sys
from topusers import users
import os
# This script gets all public tweets(including retweets) of a user.
# To run this: python tweetscraper.py <username>
# You will find a csv with a tokenized list of tweets in username.csv

API_KEYS = [
    dict(consumer_key = 'N0D7AL9QKSivv5Ogrbunxg',
         consumer_secret='JCf5pL8n9SiWf82cDp1rcS165HFS648vEXf5W5g0',
         access_token_key = '984137052-8qrvCtFTi7GAXRVRyhWhAthBzBuldBK9ETYAOHE',
         access_token_secret = 'u7bPrucjteHBRsKhOw8wpOWmWMKCTAk34YDaKtcX6sA'),

    dict(consumer_key = '7i7MFfbiHCP4E7i1l9S2g',
         consumer_secret='jGwDVgkdFu7GZIntPnyBq7wSgtTurtlYwvXAfRbxCPY',
         access_token_key = '15202847-lOjmNyFbxjImFOESPjGDue7mVgYuy9868Aghzurw',
         access_token_secret = 'XK0wDtdYfTW77bKv8RuQD1lqXuVpilaYCoEZ3YohUA'),
]

CUR_KEY = 0 

api = twitter.Api(consumer_key = API_KEYS[CUR_KEY]['consumer_key'],
                   consumer_secret = API_KEYS[CUR_KEY]['consumer_secret'],
                   access_token_key = API_KEYS[CUR_KEY]['access_token_key'],
                   access_token_secret = API_KEYS[CUR_KEY]['access_token_secret'])

users = [username.lower() for username in users]
for i in xrange(149, 500):
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
