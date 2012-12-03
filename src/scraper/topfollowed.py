import json
import re
from urllib2 import urlopen

file = open("topusers.py", "w")
matcher = re.compile(".*\((.*)\)</a>")
website = urlopen("http://twitaholic.com/top100/followers/").read()

users = []
for i in range(1, 11):
    website = "http://twitaholic.com/top%d00/followers/" % i
    text = urlopen(website).read()
    found = matcher.findall(text) 
    users.extend(found)

print len(users)
json.dump(users, file)
