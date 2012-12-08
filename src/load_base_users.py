#!/usr/bin/env python
from mongo_models import db, User
import multiprocessing as mp
from pprint import pprint

def main():

    users  = (u.get("username") for u in db.users.find() if u.get("username") and u.get("username"))
    results = mp.Pool(4).map(do_work, users)
    pprint(results)

def do_work(username):
    print username
    try:
	print "processing:", username
        User.similar_documents(username)
	print "success!"
        return ('success', username)
    except Exception as err:
	print "failed"
        return ('failure', username, err)

if __name__ == '__main__':
    main()


	    
    

 
