import twitter
import csv
import string
import sys
from topusers import users
import os
import pymongo
import re
import nltk
from collections import Counter

stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords.add("http")
stopwords.add("rt")
stopwords.add("co")

def tokenize(s):
    return [w for w in re.findall('\w+', s.lower()) if w not in stopwords]

conn = pymongo.Connection()
db = conn.tpro

# This script gets all public tweets(including retweets) of a user.
# To run this: python tweetscraper.py <username>
# You will find a csv with a tokenized list of tweets in username.csv



API_KEYS = [
    dict(consumer_key = 'N0D7AL9QKSivv5Ogrbunxg',
         consumer_secret = 'JCf5pL8n9SiWf82cDp1rcS165HFS648vEXf5W5g0',
         access_token_key = '984137052-8qrvCtFTi7GAXRVRyhWhAthBzBuldBK9ETYAOHE',
         access_token_secret = 'u7bPrucjteHBRsKhOw8wpOWmWMKCTAk34YDaKtcX6sA'),

    dict(consumer_key = '7i7MFfbiHCP4E7i1l9S2g',
         consumer_secret = 'jGwDVgkdFu7GZIntPnyBq7wSgtTurtlYwvXAfRbxCPY',
         access_token_key = '15202847-lOjmNyFbxjImFOESPjGDue7mVgYuy9868Aghzurw',
         access_token_secret = 'XK0wDtdYfTW77bKv8RuQD1lqXuVpilaYCoEZ3YohUA'),

    dict(consumer_key = 'gc2SkZvfXSXmUlSEho5ExA',
         consumer_secret = '8KGn8WWtopHHAZRDUnS4ox7BL4ZjoeNvkNptBVfQE',
         access_token_key = '984311989-3h77qDxB3fYdwIetU0gWGG6UXEpsxVlh2FzSppqu',
         access_token_secret = 'YdL8xjY2xRjFehrOJyW1zCULb35GxxaA07vrrkWNM'),

    dict(consumer_key = '49IshplCLGu9NTGQXnA1w',
         consumer_secret = 'i1oMfcMz46wTUZXZNjfbJ5ukBkeASZcWg3Xxy2JlEVI',
         access_token_key = '984322344-TKU7vaGGjdO3yQWNSObXBhq6M1Qj2mFQqUcLWig0',
         access_token_secret = 'PzauR6sGzO0K5zNvREkpE0EZfFvW4ryQnnKK9Mm4Hc'),

    dict(consumer_key = 'i8mfMI2Q55Vkl5Rm6yhzqA',
         consumer_secret = '6lrR70b4dxzzOtyjmyxv2BM6KVYqaM0B9gPZmWhsM',
         access_token_key = '984391231-PISPNFog2eV6vijsvypY7a5K0P8g0LwU0oSFoYY4',
         access_token_secret = 'cCYfpfGhAP7UTwbu2vZutvWRl1m53BgX6GchVfQEJs'),

    dict(consumer_key = '1Ie2twFjgCBgXHN0exqt0w',
         consumer_secret = 'p9twG27V1jwIghnwvZjTJjv4vqvPyxPOw5eYwX9n6c',
         access_token_key = '18520837-AvWGTxxRABDYVkRZnXW3hBKkwPuJZvgKlm8gj5Qiy',
         access_token_secret = '0retdPbMjUCT6SLJcTyH1ZABb8W0e1mTB2eoO5zULY'),

    dict(consumer_key = 'WoD9ZEJQ3W6t3IuNGO5tg',
         consumer_secret = '3aLxtwK8Vn2jxji1yrdzCKfNZ0vZFlwwMiQgtGWSIaY',
         access_token_key = '18520837-xHRE0KuG67MDWhCQeKQliHdGtuyI0Ahfz8I4fpFPk',
         access_token_secret = 'OFvGTCa7g1ftjrkjMeWtaAqHgW67MftNmuYArSXAs8'),

    dict(consumer_key = 'iegvJ0Fk7saiSi2keoVyg',
         consumer_secret = 'BCpU5IWJrUcsFONXqVuZkGeboceHxmfd8fymilCs',
         access_token_key = '985298258-XrR0gWhjujENEHE0dQ5UgYL4hL1twcl05cxHJXEd',
         access_token_secret = '9UUyQaC7cCBcM81ipuKNNA3ftz3WuwmrdMwG5B3SUA')
]

CUR_KEY = -1
NUM_ROLLS = 0
api = None
def ROLL_KEY():
    global CUR_KEY, NUM_ROLLS, api
    CUR_KEY = (CUR_KEY + 1) % len(API_KEYS) + 1
    NUM_ROLLS += 1

    # break if we've rolled more than number of API_KEYS, so it doesn't get stuck in an infiniteloop
    if NUM_ROLLS > len(API_KEYS):
        sys.exit("ALL KEYS ARE RATE-LIMITED")
    print "CUR_KEY: %d" % CUR_KEY
    api = twitter.Api(consumer_key = API_KEYS[CUR_KEY]['consumer_key'],
                       consumer_secret = API_KEYS[CUR_KEY]['consumer_secret'],
                       access_token_key = API_KEYS[CUR_KEY]['access_token_key'],
                       access_token_secret = API_KEYS[CUR_KEY]['access_token_secret'])
ROLL_KEY()

users = [username.lower() for username in users]

def scrape_friends_timelines(username):
    #number_of_friends = api.GetUser(username).friends_count

    user_record = db.users.find_one({"username":username})
    if user_record is None:
        scrape_user_timeline(username)
        user_record = db.users.find_one({"username":username})
    
    if user_record.get("friends"):
        return
    else:
        user_record["friends"] = []
        
    friends = api.GetFriends(user=username)
    friend_records = []
    for friend in friends:
        friend_name = friend.screen_name.lower()
        print friend_name
        friend_record = db.users.find_one({"username":friend_name})
        if not friend_record:
            print "found a new friend"
            friend_record = {"username": friend_name, "tweets":[], "features": Counter(), "friends": []}
        else:
            friend_record["features"] = Counter(friend_record["features"])
        if not friend.protected:
            user_record["friends"].append(friend_name)
            try:
                statuses = api.GetUserTimeline(friend.id, count=200, include_rts=True)
            except twitter.TwitterError as e:
                ROLL_KEY()
            for status in statuses: 
                status_text = status.text.encode('ascii', 'ignore')
                friend_record["tweets"].append(status_text)
                for token in tokenize(status_text):
                    friend_record["features"][token] += 1
            friend_records.append(friend_record)
            db.users.insert(friend_record)
            #db.users.update({"username": friend_record["username"]}, {"$set": {"friends": friend_record.get("friends", []), "features": friend_record["features"], "tweets": friend_record["tweets"]}})
    db.users.update({"username": user_record["username"]}, {"$set" : {"friends": user_record["friends"], "features": user_record["features"], "tweets": user_record["tweets"]}})
                

def scrape_user_timeline(username):
    data = []
    max_id = None

 
    print "hello this line is before statuses"
    print username
    statuses = api.GetUserTimeline(username, count = 200, include_rts = True)
    print "hello I'm past the call to the API"

    for status in statuses:
        print status.text, status.id
        data.append(status.text)
        max_id = status.id

    if data:
        user = {"username": username, "tweets":[], "features": Counter() }
        for tweet in data:
            user["tweets"].append(tweet)
            for token in tokenize(tweet):
                user["features"][token] += 1
        print user
        db.users.insert(user)
            
            
def scrape_to_csv(users):
#failed indices: 381, 504, 583, 625, 897, 912
    for i in xrange(1005, len(users)):
        print "User: %s, Index: %d" % (users[i], i)
    data = []
    max_id=None
    while True:
        try:
            statuses = api.GetUserTimeline(users[i], count = 200, max_id = max_id, include_rts = True)
        except twitter.TwitterError as e:
            print e
            ROLL_KEY()
            continue

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


if __name__ == '__main__':
    print "hellp"
    scrape_friends_timelines("sankethkatta")
