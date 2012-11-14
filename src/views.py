from flask import Flask, render_template, request
from twitter_utils import hard_data
import search_engine
import os
import json
from collections import Counter, defaultdict
import numpy
app = Flask(__name__)
s_engine = search_engine.main()

@app.route('/')
def index():
    # Load pre-fetched data from Twitter api 
    image_urls = {"politics": hard_data.politics_image_urls,
                  "sports": hard_data.sports_image_urls}

    return render_template('index.html', image_urls=image_urls, home_active="active")

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == "POST":
        similarity = s_engine.query(request.form['query'])
        to_client = []
        averages = defaultdict(list)
        for score in similarity:
            file = os.path.split(score[1])
            folder = os.path.split(file[0])
            to_client.append({"industry": folder[1], "user": file[1].strip(".csv"), "score": score[0]})
            averages[folder[1]].append(score[0])

        # NOTE this doesn't take the average score over all the people in a particular industry, but
        # rather the average of the people in the industry that matched your query
        for industry, values in averages.iteritems():
            to_client.append({"industry": industry, "user": "average", "score" :numpy.average(values)})
            
        return json.dumps(to_client)
    else:
        return render_template('analyze.html', analyze_active="active")

@app.route('/about')
def about():
    return render_template('about.html', about_active="active")

@app.route('/methodology')
def methodology():
    return render_template('methodology.html', methodology_active="active")

if __name__ == '__main__':
    app.run(debug=True)
