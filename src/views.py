from flask import Flask, render_template, request
import search_engine
import os
import json
from collections import Counter, defaultdict
import numpy
from twitter_utils import topuserimageslower, hard_data
from mongo_models import *
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
#s_engine = search_engine.main()

@app.route('/')
def index():
    # Load pre-fetched data from Twitter api 
    image_urls = {"politics": hard_data.politics_image_urls,
                  "sports": hard_data.sports_image_urls}

    return render_template('index.html', image_urls=image_urls, home_active="active")

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == "POST":
        #similarity = s_engine.query(request.form['query'])
        query = request.form['query']
        print query
        results = User.similar_documents(query)
        to_client = []
        averages = defaultdict(list)
        for score, username in results:
            to_client.append({"user": username, "img": topuserimageslower.urls[username] })
            
	print to_client
        return json.dumps(to_client)
    else:
        return render_template('analyze.html', analyze_active="active")

@app.route('/about')
def about():
    return render_template('about.html', about_active="active")

@app.route('/methodology')
def methodology():
    return render_template('methodology.html', methodology_active="active")

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
