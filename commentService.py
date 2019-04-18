from flask import Flask, jsonify, request, make_response,g,Response
import sqlite3
import re
from passlib.hash import sha256_crypt
from flask_api import status
from flask_httpauth import HTTPBasicAuth
import datetime
from http import HTTPStatus
from functools import wraps

app = Flask(__name__)
auth = HTTPBasicAuth()

microservice_database = 'comment_database.db'
microservice_database1 = 'article_database.db'

def get_database():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(microservice_database)
        database.cursor().execute("PRAGMA foreign_keys = ON")
        database.commit()
    return database

def get_database1():
    database = getattr(g, '_database1', None)
    if database is None:
        database = g._database1 = sqlite3.connect(microservice_database1)
        database.cursor().execute("PRAGMA foreign_keys = ON")
        database.commit()
    return database

@app.teardown_appcontext
def close_connection(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

def authenticate_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global author
        auth = request.authorization
        if not auth:
            author = 'Anonymous Coward'
        elif not verify(auth.username, auth.password):
            return Response(status=401, mimetype='application/json')
        else:
            author= auth.username
        return f(*args, **kwargs)
    return decorated

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route("/addcomment/<articletitle>", methods=['POST'])
#@authenticate_user
def add_comment(articletitle):
    if (request.method == 'POST'):
        try:
            db = get_database()
            c = db.cursor()

            db1 = get_database1()
            c1 = db1.cursor()

            comment_details = request.get_json()
            author = request.authorization.username
            if not request.json.get('comment'):
                return jsonify("Please enter comment on articles")
            else:
                c1.execute("select article_id,article_author from articles_table where article_title = (:title) COLLATE NOCASE", {'title': articletitle})
                row_id = c1.fetchone()
                if row_id:
                    id = row_id[0]
                    article_author = row_id[1]
                else:
                    return Response(status=404, mimetype='application/json')
                c.execute("insert into comments_table (comment, username, article_id, article_title, article_author, createdDate) values (?,?,?,?,?,?)",
                                    [comment_details['comment'], author, id,articletitle,article_author, datetime.datetime.now()])
                db.commit()
                c.execute("select comment_id from comments_table order by createdDate desc limit 1")
                row = c.fetchone()
                if row:
                    commentid = row[0]
                else:
                    return Response(status=404, mimetype='application/json')
                response_message = Response(status=201, mimetype='application/json')
                response_message.headers['location'] = 'http://127.0.0.1:5000/addcomment/'+articletitle+str(commentid)

        except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')

    return response_message

@app.route("/deletecomment", methods=['DELETE'])
#@auth.login_required
def delete_comment():
    if (request.method == 'DELETE'):
        response_message = ""
        try:
            db = get_database()
            c = db.cursor()
            # db1 = get_database1()
            # c1 = db1.cursor()
            comment_details = request.get_json()
            c.execute("select comment_id from comments_table where comment_id=(:id)",{"id":comment_details['id']})
            row = c.fetchone()
            if (row == None ):
                response_message = Response(status=404, mimetype='application/json')
                return response_message
            # else:
                # c1.execute("select article_author from articles_table where article_id = (select article_id from comments_table where comment_id=(:id))",{"id":comment_details['id']})
                # temp = c1.fetchone()
                # print(temp)
                # c.execute("select username from comments_table where comment_id=(:id)",{"id":comment_details['id']})
                # row_username = c.fetchone()
                # print(row_username[0])
                # print(temp[0])
                # print(request.authorization.username)
                #if(request.authorization.username == row_username[0] or request.authorization.username == temp[0] or row_username[0] == 'Anonymous Coward'):
            c.execute("delete from comments_table where comment_id=(:id) and (article_author=(:author) OR username=(:author))",{"id":comment_details['id'],"author":request.authorization.username})
            db.commit()
            if(c.rowcount == 1):
                response_message = Response(status=200, mimetype='application/json')
            else:
                response_message = Response(status=404, mimetype='application/json')
                #else:
                #    response_message = Response(status=401, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')

    return response_message

@app.route("/comments/count/<articletitle>", methods=['GET'])
def retrieve_comment(articletitle):
    if (request.method == 'GET'):
        try:
            db = get_database()
            c = db.cursor()
            c.execute("select article_id from comments_table where article_title = (:title) COLLATE NOCASE", {'title': articletitle})
            row_id = c.fetchone()

            if (row_id == None ):
                return Response(status=404, mimetype='application/json')

            c.execute("select count(comment_id) from comments_table where article_title=(:articletitle)",{"articletitle":articletitle})
            row_comment_id = c.fetchone()
            if row_comment_id:
                return "Number of comments for " + articletitle + " is " + str(row_comment_id[0]) + ".\n"
            else:
                response_message = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')

    return response_message

@app.route("/retrieveArticle/<articletitle>/<recentcomments>", methods=['GET'])
def recentcomments(articletitle,recentcomments):
    try:
        db = get_database()
        c = db.cursor()
        c.execute("select article_id from comments_table where article_title = (:title) COLLATE NOCASE", {'title': articletitle})
        row_id = c.fetchone()

        if (row_id == None ):
            return Response(status=404, mimetype='application/json')


        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("select comment from comments_table where article_id=(:articleid) order by comment_id desc limit (:recent)", {"articleid":row_id[0], "recent":recentcomments})
        row_id_comment = c.fetchall()
        print(row_id_comment)
        if row_id_comment:
            return jsonify(row_id_comment)
        else:
            response_message = Response(status=404, mimetype='application/json')

    except sqlite3.Error as er:
        print(er)
        response_message = Response(status=409, mimetype='application/json')

    return response_message

if __name__ == '__main__':
    app.run(debug=True)
