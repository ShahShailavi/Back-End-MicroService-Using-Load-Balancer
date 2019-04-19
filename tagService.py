from flask import Flask, jsonify, request, make_response,g,Response
import sqlite3
import re
from passlib.hash import sha256_crypt
from flask_api import status
from flask_httpauth import HTTPBasicAuth
import datetime
from http import HTTPStatus

app = Flask(__name__)
auth = HTTPBasicAuth()

tag_database = 'tag_database.db'
article_database='article_database.db'

def get_database(dbnamae):
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(dbnamae)
        database.commit()
    return database

def get_database1(dbnamae):
    database = getattr(g, '_database1', None)
    if database is None:
        database = g._database1 = sqlite3.connect(dbnamae)
        database.commit()
    return database

@app.teardown_appcontext
def close_connection(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# To add new article with tag or to add new tags for existing article
@app.route("/tag/addtag", methods=['POST'])
def addTags():
    if (request.method == 'POST'):
        db = get_database(tag_database)
        c = db.cursor()
        c1=get_database1(article_database).cursor()
        details = request.get_json()
        update_time = datetime.datetime.now()
        email = request.authorization.username

        try:
            tag_Details=details['tag'].split(',')
            articleId=request.json.get('articleId')
            if (not request.json.get('articleId')):
                if not request.json.get('articletitle'):
                    return jsonify("You can not create blog without article title")
                elif not request.json.get('articlecontent'):
                    return jsonify("You can not create blog without article content")
                temp = str(details['articletitle'].replace(" ", "%20"))
                temp = 'http://127.0.0.1:5000/retrieveArticle/' + temp
                c1.execute("insert into articles_table (article_title, article_content, article_author, createdDate, modifiedDate, URL) values (?,?,?,?,?,?)",[details['articletitle'], details['articlecontent'], request.authorization.username,datetime.datetime.now(), datetime.datetime.now(), temp])
                articleId=c1.lastrowid
                print(articleId)
                db.commit()
            else:
                c1.execute("SELECT article_id FROM articles_table WHERE article_id=?", (articleId,))
                rec = c1.fetchone()
                for tags in tag_Details:
                    tag=tags.strip()
                    print(tag)
                    c.execute("SELECT tagId FROM tag_master WHERE tagName=?",(tag,))
                    print("hi")
                    rec=c.fetchall()
                    #rowsaffected=len(rec)
                    if not rec:
                        print("hi")
                        c.execute("INSERT INTO tag_master (tagName,createdTime,updatedTime) VALUES (?,?,?)",(tag,datetime.datetime.now(), datetime.datetime.now(),))
                        db.commit();
                        print("hi")
                        c.execute("SELECT tagId FROM tag_master WHERE tagName=?",(tag,))
                        rec2=c.fetchall()
                        tid=rec2[0][0]
                        c.execute("INSERT INTO tag_detail (article_id,tagId,createdTime,updatedTime) VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now(),))
                        db.commit();
                    else:
                        print("inside else")
                        tid=rec[0][0]
                        c.execute("INSERT INTO tag_detail VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now()))

                    if (c.rowcount == 1):
                        db.commit()
                        response = Response(status=201, mimetype='application/json')

                    else:
                        response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response


#Delete a tag
@app.route("/tag/deletetag", methods=['DELETE'])
def deletetag():
    if (request.method == 'DELETE'):
        try:
            db = get_database(tag_database)
            c = db.cursor()
            details = request.get_json()
            artid= details['articleId']
            tag=details['tag']
            print(tag)
            #for tag in tags:
            print("in for loop" + str(artid))
            c.execute("DELETE FROM tag_detail WHERE article_id=? AND tagId IN (SELECT tagId FROM tag_master WHERE tagName=?)",(artid,str(tag),))
            db.commit()
            if (c.rowcount == 1):
                db.commit()
                response = Response(status=200, mimetype='application/json')
            else:
                response = Response(status=404, mimetype='application/json')
        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response


#Retrive Tags for article id
@app.route("/tag/gettag/<artid>", methods=['GET'])
def getarticle(artid):
    if (request.method == 'GET'):
        try:
            db = get_database(tag_database)
            db.row_factory = dict_factory
            c = db.cursor()
            c.execute("SELECT * FROM tag_master WHERE tagId IN (SELECT tagId FROM tag_detail WHERE article_id=?)",(artid,))
            row = c.fetchall()
            db.commit()
            print(row)
            if row is not None:
                return jsonify(row)
            else:
                response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response

# get all the articles for a specific tag
@app.route('/tag/getarticles/<tag>',methods=['GET'])
def getart(tag):
    try:
        db = get_database(tag_database)
        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("SELECT article_id FROM tag_detail WHERE tagId IN (SELECT tagId FROM tag_master WHERE tagName=?)",(tag,))
        row = c.fetchall()
        #add code to get url for articles

        if row is not None:
            return jsonify(row)
        else:
            response = Response(status=404, mimetype='application/json')

    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response

if __name__ == '__main__':
    app.run(debug=True)
