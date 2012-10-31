#!/usr/bin/env python
from collections import defaultdict
import re
import pprint
import operator
import os
from math import sqrt

pp = pprint.PrettyPrinter(indent=2)

class Vector(dict):

  def build_from_query(self, query):
    for w in (s.lower() for s in re.findall('\w+', query)):
      self[w] = self.get(w, 0.0) + 1.0
    
  def dot_product(self, other):
    v1 = self
    v2 = other
    v3 = Vector()
    key_union = set(v1.keys()) | set(v2.keys())
    for key in key_union:
      v3[key] = v1.get(key, 0.0) * v2.get(key, 0.0)
    return sum(v for (k,v) in v3.iteritems())
      
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
      self._index = defaultdict(lambda : defaultdict(float))

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        words = [w.lower() for w in re.findall('\w+', f.read())]
        for w in words:
          self._index[fname][w] += 1.0

  def query(self, query, k=10):
    query_vector = Vector()
    query_vector.build_from_query(query)
    return sorted(((query_vector.cosine_similarity(Vector(term_vector)), doc) for (doc, term_vector) in self._index.iteritems()), reverse=True)[:k]

class InvertedIndex(BaseIndex):
  
  def __init__(self):
    self._index = defaultdict(set)

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        words = [w for w in re.findall('\w+', f.read().lower())]
        for w in words:
          self._index[w].add(fname)

  
  def query(self, query, k=10):
    words = [w for w in re.findall('\w+', query.lower())]
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
  search_engine = SearchEngine(InvertedIndex())
  data_folder = [os.path.join('data', fname) for fname in os.listdir('data')]
  search_engine.build(data_folder)
  while True:
    try:
      query = raw_input("Enter a query: ")
      if query == "show_index":
        pp.pprint(dict(search_engine.index._index))
      else:
        pp.pprint(search_engine.query(query))
    except Exception as err:
      print err
      print '\nGoodbye'
      exit()
    
