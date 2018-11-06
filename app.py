import os

import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import matplotlib
matplotlib.use('Agg')

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask ,url_for,render_template,request,abort



app = Flask(__name__)


comment_words = ' '
stopwords = set(STOPWORDS)
cloud_words = ' '


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/cloud/<max>")
def cloud_image(max):
    maxVal = int(max)
    create_cloud(maxVal)
    filename = 'cloud.png'
    return send_file(filename, mimetype='image/png')

def create_cloud(max):
    global cloud_words
    global comment_words
    cloud_words = ' '
    comment_words = ' '
    url = "https://s3.amazonaws.com/quicksight.mlvisualizer.com/data/mail-data-for-visualization.json"
    result = pd.read_json(url, orient='records')
    dataList = result.dataList
    dataList = dataList[:max]
    for data in dataList:
        # print(data)
        keywords = data['keywords']
        for keyword in keywords:
            # print(str(keyword['name']) + ':' + str(keyword['count']))
            # wordCount = int(keyword['count'])
            # print("wordCount: " + str(wordCount))
            # while wordCount > 0:
            #     cloud_words = cloud_words + ' ' + str(keyword['name'])
            #     wordCount = wordCount - 1
            cloud_words = cloud_words + ' ' + str(keyword['name'])
            tokens = cloud_words.split()
            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()

            for words in tokens:
                comment_words = comment_words + words + ' '

    try:
        # generate cloud
        wordcloud = WordCloud(width = 600, height = 400,
                              background_color ='white',
                              stopwords = stopwords,
                              min_font_size = 10).generate(comment_words)

        # plot the WordCloud image
        plt.figure(figsize = (5, 5), facecolor = None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        imageFile = "cloud.png"
        plt.savefig(imageFile, dpi=100,
                    bbox_inches='tight')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=5000)
