import csv
import string
import sys
import os
import re

from topusers import users

users = [username.lower() for username in users]

hash = {}

for user in users:
	csvFileName = os.path.join('topuserbios', user + ".csv")
	try:
		with open(csvFileName, 'rb') as f:
				reader = csv.reader(f)
				for row in reader:
					hash[user] = row[1]
	except:
		pass
		#print user

print hash
