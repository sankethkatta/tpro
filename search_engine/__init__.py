#!/usr/bin/env python
from collections import defaultdict, Counter
import re
import pprint
import operator
import os
from math import sqrt

pp = pprint.PrettyPrinter(indent=2)

def tokenize(query):
  return re.findall('\w+', query.lower())

class Vector(Counter):

  def build_from_query(self, query):
    self.build_from_list(tokenize(query))

  def build_from_list(self, lst):
    for w in lst: 
      self[w] += 1.0
    
  def dot_product(self, other):
    v1, v2 = self, other
    keys = set(v1.keys()) | set(v2.keys())
    return reduce(operator.add, (v1[key] * v2[key] for key in keys))
      
  def cosine_similarity(self, other):
    dot_product = self.dot_product(other)
    try:
      return dot_product / (self.magnitude()*other.magnitude())
    except ZeroDivisionError:
      return 0
      
    

  def __div__(self, c):
    try:
      return Vector((key, value/c) for (key,value) in self.iteritems())
    except ZeroDivisionError:
      raise ZeroDivisionError("Cannot divide by zero")

  def normalize(self):
    return self/self.magnitude()

  def magnitude(self):
    return sqrt(sum(v*v for v in self.itervalues()))

class BaseIndex(object):

  def build(self, fnames):
    raise NotImplementedError

  def query(self, query, k=10):
    raise NotImplementedError


class ForwardIndex(BaseIndex):
  
  def __init__(self):
      self._index = defaultdict(Vector)

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        words = tokenize(f.read())
        for w in words:
          self._index[fname][w] += 1.0

  def query(self, query, k=10):
    query_vector = Vector()
    query_vector.build_from_query(query)
    return sorted(((query_vector.cosine_similarity(term_vector), doc) for (doc, term_vector) in self._index.iteritems()), reverse=True)[:k]

class InvertedIndex(BaseIndex):
  
  def __init__(self):
    self._index = defaultdict(set)

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        words = tokenize(f.read())
        for w in words:
          self._index[w].add(fname)

  
  def query(self, query, k=10):
    words = tokenize(query)
    candidates = self._index[words[0]]
    for w in words:
      candidates &= self._index[w]
    return [c for c in candidates][:k]
      



class SearchEngine(object):

  def __init__(self, index):
    self.index = index

  def build(self, fnames):
    self.index.build(fnames)

  def query(self, query, k=10):
    return self.index.query(query, k=k)
    
    
if __name__ == '__main__':
  search_engine = SearchEngine(ForwardIndex())
  data_folder = [os.path.join('data', fname) for fname in os.listdir('data')]
  search_engine.build(data_folder)
  while True:
    try:
      query = raw_input("Enter a query: ")
      pp.pprint(search_engine.query(query))
    except Exception as err:
      print err
      print '\nGoodbye'
      exit()
    
