import sqlite3
connection = sqlite3.connect('tag_database.db')
c = connection.cursor()
c.execute("""CREATE TABLE tag_master (
                    tagId INTEGER PRIMARY KEY AUTOINCREMENT,
                    tagName TEXT,
                    createdTime DATETIME,
                    updatedTime DATETIME)""")

c.execute("""CREATE TABLE tag_detail (
                    article_id INTEGER,
                    tagId INTEGER NOT NULL REFERENCES tag_master(tagId),
                    createdTime DATETIME,
                    updatedTime DATETIME,
                    PRIMARY KEY(article_id,tagId)
                    )""")


connection.commit()
connection.close()
