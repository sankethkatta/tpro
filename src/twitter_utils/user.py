from twython import Twython
from topusers import users
import json

t = Twython(app_key='fxmq7LkdyUpQbTh72zqTA',
            app_secret='kSNCIvAOZxy4zipLzNWJxjPQ9KvOROaX1HTwHjufdc',
            oauth_token='15202847-lOjmNyFbxjImFOESPjGDue7mVgYuy9868Aghzurw',
            oauth_token_secret='XK0wDtdYfTW77bKv8RuQD1lqXuVpilaYCoEZ3YohUA')

file = open("topuserimages.py", "w")
def get_profileimage_urls(users):
    """
    Input: list of twitter handles
    Output: dictionary of each handle as a key, urls as values
    """
    urls = {}
    for user in users:
        try:
            urls[user] = (t.getProfileImageUrl(user, size="bigger"))
        except:
            pass
        print user
    json.dump(urls, file)

if __name__ == "__main__":
    get_profileimage_urls(users)
