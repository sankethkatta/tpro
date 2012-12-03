#!/usr/bin/env python
from collections import Counter, defaultdict
import cPickle
import nltk
import os
import csv
import re
from stemming.porter import stem

stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords = stopwords | set(['http', 'rt', 'co', 'com'])

def tokenize(s):
    return [w for w in re.findall('\w+', s.lower()) if w not in stopwords]


def build_table():
    table = defaultdict(Counter)
    csvs = [f for f in os.listdir('.') if f.endswith('.csv')]
    for fname in csvs:
        with open(fname, 'rb') as f:
            reader = csv.reader(f)
            for username, tweet in reader:
                for s in (stem(t) for t in tokenize(tweet)):
                    table[username][s] += 1
    return table

if __name__ == '__main__':
    cPickle.dump(table, 'search_index.cpickle')
                        

