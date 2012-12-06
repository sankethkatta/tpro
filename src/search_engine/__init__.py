#!/usr/bin/env python
from collections import defaultdict, Counter
import re
import pprint
import operator
import os
import pickle
from math import sqrt, log

pp = pprint.PrettyPrinter(indent=2)

def tokenize(query):
  return re.findall('\w+', query.lower())

class Vector(Counter):

  def build_from_query(self, query):
    self.build_from_list(tokenize(query))

  def build_from_list(self, lst):
    for w in lst: 
      self[w] += 1.0

  def build_tf_idf(self, query, index):
    self.build_from_query(query)

    for term in self.iterkeys():
      self[term] *= index.idf(term)

  def __add__(self, other):
      return Vector(Counter.__add__(self, other))

  def dot_product(self, other):
    v1, v2 = self, other
    #keys = set(v1.keys()) | set(v2.keys())
    keys = set()
    for key in v1.iterkeys(): keys.add(key)
    for key in v2.iterkeys(): keys.add(key)
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


class ForwardIndex(BaseIndex):
  
  def __init__(self):
      self._index = defaultdict(Vector)
      self._vectors = defaultdict(Vector)

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        for line in f:
          words = tokenize(line)
          for w in words[1:]:
            self._index[fname][w] += 1.0

    for fname in self._index.iterkeys():
      for w in self._index[fname]:
        self._vectors[fname][w] = self.tf_idf(w, fname)

  def query(self, query, candidates=None, k=10):
    query_vector = Vector()
    query_vector.build_tf_idf(query, self)
    
    if candidates is None:
      candidates = self._vectors.iterkeys()

    return sorted(((query_vector.cosine_similarity(self._vectors[doc]), doc) for doc in candidates), reverse=True)[:k]

  def tf(self, term, doc):
    """ Returns the count of :param term: in :param doc: """
    return max(self._index[doc][term], 1.0)
    
    
  def number_documents(self):
    """ Returns the total number of documents stored in the index"""
    return len(self._index)

  def idf(self, term):
    """ Returns inverse-document-frequency of a given term """
    return self.number_documents()/max(1.0, sum(float(term in self._index[doc]) for doc in self._index.iterkeys()))

  def tf_idf(self, term, doc):
    """ Returns the tf_idf score for :param term: and :param doc:"""
    return self.tf(term, doc)*log(self.idf(term))


class InvertedIndex(BaseIndex):
  
  def __init__(self):
    self._index = defaultdict(set)

  def build(self, fnames):
    for fname in fnames:
      with open(fname, 'r') as f:
        for line in f:
          words = tokenize(line)
          for w in words[1:]:
            self._index[w].add(fname)

  
  def candidates(self, query):
    words = tokenize(query)
    
    # this needs to be a COPY of the list, or else we'll overwrite previous values
    candidates = set(self._index[words[0]]) if words else set() 
    for w in words:
      # let a candidate be a document with at least one of the query terms, we'll get better results this way
      candidates |= self._index[w]          
    return [c for c in candidates]


class SearchEngine(object):

  def __init__(self, findex, iindex):
    self.forward_index = findex
    self.inverted_index = iindex

  def build(self, fnames):
    self.forward_index.build(fnames)
    self.inverted_index.build(fnames)

  def query(self, query, k=10):
    candidates = self.inverted_index.candidates(query)
    return self.forward_index.query(query, candidates=candidates, k=k)
    
def main():

  DATA_DIRECTORY = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'data')
  path_to_pickle = os.path.join(DATA_DIRECTORY, 'search_engine.data')
  # attempt to find pickled search engine
  try:
    with open(path_to_pickle, 'r') as f:
      search_engine = pickle.load(f)
      print "Search engine loaded from pickle"
      return search_engine
  except IOError:
    pass

  print "Building the search engine"
  # build the search engine the normal way
  search_engine = SearchEngine(ForwardIndex(), InvertedIndex())
  
  section_folders = [os.path.join(DATA_DIRECTORY, dname) for dname in os.listdir(DATA_DIRECTORY)]
  data_folder = []
  for folder in section_folders:
    data_folder.extend([os.path.join(folder, fname) for fname in os.listdir(folder)])
  search_engine.build(data_folder)

  # save a pickled copy of the search engine in a data file
  with open(path_to_pickle, 'wb') as f:
    pickle.dump(search_engine, f)
  
  return search_engine
    
if __name__ == '__main__':
  search_engine = main()
  while True:
    try:
      query = raw_input("Enter a query: ")
      pp.pprint(search_engine.query(query))
    except Exception as err:
      print err
      print '\nGoodbye'
      exit()
    
