import hashlib
import sqlite3

from werkzeug.security import generate_password_hash

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

psw = generate_password_hash("1234")

cur.execute("INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)",
            ('lemur', 'lemur@gmail.com', psw)
            )

cur.execute("INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)",
            ('First Post', 'Content for the first post', 'img/6fcca2f2.png', 'lemur')
            )

cur.execute("INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)",
            ('Second Post', 'Content for the second post', 'img/30f45075.png', 'lemur')
            )

cur.execute("INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)",
            ('Third Post', 'Content for the second post', 'img/982abf10.png', 'lemur')
            )

connection.commit()
connection.close()
