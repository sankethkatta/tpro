#!/usr/bin/env python
import os
import time
import random
import sys
from mongo_models import db, User

##############################################################################
##
##  Usage: python scrape_common_users <file_name_in_scraper/split_user_files>
##  
##############################################################################

def main(fname):
    full_name = os.path.join('scraper/split_user_files', fname)
    print full_name
    success, failure = [], []
    with open(full_name, 'rb') as f:
	for line in f:
	    username = line.strip().lower()
	    print "SCRAPING OUR FRIEND:",username
	    try:
   	        User.similar_documents(username)
	    except Exception as err:
		print err
		failure.append(username)
	    print "DONE WITH:", username
	    success.append(username)
    print "SUCCESS:", success
    print "FAILURE:", failure

if __name__ == '__main__':
    main(sys.argv[1])
