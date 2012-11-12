from twython import Twython

t = Twython(app_key='RzvEfd2YnuLG4HLTamB71A',
            app_secret='23ddxWtwmXXWTfBPz3S0MJRkKXxXailx2fI40ehd2M0',
            oauth_token='15202847-wcK11pamFZO4w6pG4LHfnOtVf5YnvKHeG1voK0Y10',
            oauth_token_secret='ou7dnysvPNFjPMN5QBKnvXSjn1m490WQpOAFIdDlfQ')

def get_profileimage_urls(users):
    """
    Input: list of twitter handles
    Output: dictionary of each handle as a key, urls as values
    """
    urls = {}
    for user in users:
        urls[user] = (t.getProfileImageUrl(user, size="bigger"))

    return urls
