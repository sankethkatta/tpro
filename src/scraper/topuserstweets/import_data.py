from collections import Counter, defaultdict
import os
import csv
from stemming.porter import stem
import re
import nltk

stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords.add('http')
stopwords.add('co')
stopwords.add('com')

def tokenize(s):
    return re.findall('\w+', s)

def build_table():
    table = defaultdict(Counter)
    dirs = [fname for fname in os.listdir('.') if fname.endswith('.csv')]
    for fname in dirs:
        with open(fname, 'r') as f:
            reader = csv.reader(f)
            for username, tweet in reader:
                for token in tokenize(tweet.lower()):
                    if token not in stopwords:
                        table[username.lower()][stem(token)] += 1

    return table
