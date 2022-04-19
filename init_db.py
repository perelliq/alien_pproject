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
            ('первый отзыв',
             'Я посетил планету Вороноид в августе прошлого года и побывал на одном из вулканов, известном'
             'в научных кругах как Черная гора.'
             'Это было потрясающее зрелище - вулкан, извергающий пылающий поток лавы.'
             'Я и представить не мог, что такое вообще может быть. '
             'По мере того, как лава остывала, количество серы в ней уменьшалось.'
             ' Мне вспомнился рассказ одного моего университетского товарища о том,'
             'как лед на Красной планете становился раскаленным, и наоборот.',
             'img/6fcca2f2.png', 'perelliq')
            )

cur.execute("INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)",
            ('грустный отзыв', 'Мой отзыв о поездке на планету Вороноид будет коротким '
                               '- в нем не будет ничего личного. Она мне безразлична.  '
                               'Мой взгляд на этот мир действительно несколько неполон - на '
                               'его фоне я могу видеть мир, полный опасностей, - например, образ жизни клыкастых. '
                               ' Но я не боюсь говорить об этом. Если бы вы знали Вороноид - вам было бы нелегко.',
             'img/30f45075.png', 'perelliq')
            )

cur.execute("INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)",
            ('пост', 'Очень советую слетать на планету Вороноид - там полно жуков и '
                     'много юпитерианских жвачных. Они не только очень быстро едят, но '
                     'и очень смешные.  Могут ходить на задних ногах и кивать головами. '
                     'Они чем-то напоминают нам нас самих - хотя по своей природе они совсем другие...  '
                     'Но раз это полезная информация, я напечатаю ее на всех этих схемах, ладно?', 'img/982abf10.png',
             'perelliq')
            )

connection.commit()
connection.close()
