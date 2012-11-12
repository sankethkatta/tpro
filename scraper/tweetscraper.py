import twitter
import csv
import string
import sys

# This script gets all public tweets(including retweets) of a user.
# To run this: python tweetscraper.py <username>
# You will find a csv with a tokenized list of tweets in username.csv
api = twitter.Api(consumer_key = '723w730Htbdk4pgyb2sdEA',
                   consumer_secret='wk6CoLNX2SxxZNWvlnaDYocmp6AUtQqTUVzGC1eKlEg',
                   access_token_key = '20957704-icOHaCW6yqxJmUSamU9qMZI7t9kirpMYWKC9Ck0o',
                   access_token_secret = '4a1IA9Y0mRZs6a5CHmsFtyNw4T37xc9rgHv1Tht2UbM')
data = []
max_id = None
total = 0
usernameToAcquireTweets =  sys.argv[1]
while True:
    statuses = api.GetUserTimeline(usernameToAcquireTweets, count = 200, max_id = max_id, include_rts = True)
    total = total + len(statuses)
    print total
    for s in statuses:
        data.append(s)
        max_id = s.id
    if len(statuses) == 0:
        break
    max_id = max_id - 1

#writes to a csv
csvFileName = usernameToAcquireTweets + ".csv"
count = 0
with open(csvFileName, 'wb') as f:
    writer = csv.writer(f)
    for status in data:
        count = count + 1
        print count
        statusText = status.text.lower()
        statusText = statusText.encode('ascii', 'ignore')
        #remove punctuation
        statusText = statusText.translate(string.maketrans("", ""), string.punctuation)
        #split status into individual words
        splitStatus = statusText.split(" ")
        #remove mention of RT
        splitStatus = filter(lambda word: word != "rt", splitStatus)
        for word in splitStatus:
            if "http" not in word and word != " ": #remove mentions of links
                writer.writerow([usernameToAcquireTweets, word])
