import sqlite3
connection = sqlite3.connect('article_database.db')
c=connection.cursor()

c.execute("""create table if not exists articles_table (article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            article_title text UNIQUE,
                                            article_content text,
                                            article_author text,
                                            URL text,
                                            createdDate text,
                                            modifiedDate text)""")

connection.commit()
connection.close()
