from flask import Flask, jsonify, request, make_response,g,Response
import sqlite3
import re
from passlib.hash import sha256_crypt
from flask_api import status
from flask_httpauth import HTTPBasicAuth
import datetime
from http import HTTPStatus
import datetime
import requests

from rfeed import *

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route("/summaryfeed", methods=['GET'])
def summary():
    article_summary = requests.get('http://localhost/retrivemetadata/100')
    articles = []

    if article_summary is not None:
        article_summary = article_summary.json()

    for article in article_summary:
        articles.append(Item(
            title = article['article_title'],
            author = article['article_author'],
            link = article['URL'],
            date = article['createdDate']
        ))

    feed = Feed(
        title = "Article Summary Feed",
        link = "www.ankitsharma.com",
        description = "This is the Ankit Sharma ftom Streams Apartment number 64 from first bedroom",
        language = "en-US",
        items = articles
    )

    return feed.rss()

@app.route("/commentfeed", methods=['GET'])
def commentsummary():
    article_summary = requests.get('http://localhost/retrivenrecentarticle/100')
    articles = []

    if article_summary is not None:
        article_summary = article_summary.json()

    for article in article_summary:
        comment_array = []
        comments = requests.get('http://localhost/retrievearticle/'+article['article_title']+'/100')
        if comments is not None and comments.text != '':
            comments = comments.json()

        for comment in comments:
            comment_array.append(comment['comment'])

        articles.append(Item(
            title = article['article_title'],
            categories = comment_array
        ))

    feed = Feed(
        title = "Article-Comment Summary Feed",
        link = "www.ankitsharma.com",
        description = "This is the Ankit Sharma ftom Streams Apartment number 64 from first bedroom",
        language = "en-US",
        items = articles
    )

    return feed.rss()

app.run()
