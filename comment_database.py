import sqlite3
connection = sqlite3.connect('comment_database.db')
c=connection.cursor()

c.execute("""create table if not exists comments_table (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                             comment text,
                                             username TEXT,
                                             article_id INTEGER,
                                             article_title TEXT,
                                             article_author TEXT,
                                             createdDate text)""")

connection.commit()
connection.close()
