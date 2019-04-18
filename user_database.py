import sqlite3
connection = sqlite3.connect('user_database.db')
c=connection.cursor()
c.execute("""create table if not exists users_table(name TEXT,
                                    username TEXT PRIMARY KEY,
                                    userpassword TEXT)""")
connection.commit()
connection.close()
