from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import abort
from flask_login import LoginManager, logout_user, login_required
from flask_login import current_user, login_user
from generativepy.drawing import make_image, setup
from generativepy.geometry import Polygon
from generativepy.color import Color
from scipy.spatial import Voronoi
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import hashlib
import random
import sqlite3
import os

from datetime import datetime, timezone

SIZE = 400
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
login = LoginManager(app)
app.config['SECRET_KEY'] = 'lemur_2112'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_name(self):
        return self.username

    def get_name_from_id(self, user_id):
        return self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.String(540))
    image = db.Column(db.String(40))
    stamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    username = db.Column(db.String(140))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post_content = conn.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post_content is None:
        abort(404)
    return post_content


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM post').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post_content = get_post(post_id)
    return render_template('post.html', post=post_content)


@app.route('/create', methods=('GET', 'POST'))
def create():
    # создание пользователем нового сообщения

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # print(type(current_user))
        user = User.query.get(current_user.get_id())
        username = user.get_name()
        file_hash = make_hash(content)
        image = "img/" + file_hash + ".png"
        save_pic(file_hash)

        if not title:
            flash('Заголовок сообщения обязателен!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO post (title, content, image, username) VALUES (?, ?, ?, ?)',
                         (title, content, image, username))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


def draw(ctx, pixel_width, pixel_height, frame_no, frame_count):
    # создание рандомного изображения

    content = request.form['content'].lower()

    # генерация количества фигур в зависимости от содержания поста

    if "big" in content or "enormous" in content or "lot" in content or \
            "больш" in content or "мало" in content:
        points_number = random.randint(2, 20)
    elif "little" in content or "small" in content or "few" in content or \
            "много" in content or "маленьк" in content:
        points_number = random.randint(50, 100)
    else:
        points_number = random.randint(2, 100)

    points = [[random.randrange(SIZE), random.randrange(SIZE)]
              for _ in range(points_number)]
    points.append([-SIZE * 3, -SIZE * 3])
    points.append([-SIZE * 3, SIZE * 4])
    points.append([SIZE * 4, -SIZE * 3])
    points.append([SIZE * 4, SIZE * 4])

    setup(ctx, pixel_width, pixel_height, background=Color(random.random()))
    voronoi = Voronoi(points)
    voronoi_vertices = voronoi.vertices

    for region in voronoi.regions:
        if -1 not in region:
            line = random.randint(0, 8)
            polygon = [voronoi_vertices[i] for i in region]

            # генерация цветов в зависимости от содержания поста

            if "black" in content or "gray" in content or "white" in content \
                    or "чёрн" in content or "сер" in content or "бел" in content:
                color = random.random()
                ctx.set_source_rgba(color, color, color)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(random.random()))
            elif "blue" in content or "голуб" in content or "син" in content:
                color = random.random()
                ctx.set_source_rgba(0, 0, color)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(0, 0, random.random()))
            elif "green" in content or "зелен" in content or "зелён" in content:
                color = random.random()
                ctx.set_source_rgba(0, color, 0)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(0, random.random(), 0))
            elif "red" in content or "красн" in content:
                color = random.random()
                ctx.set_source_rgba(color, 0, 0)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(random.random(), 0, 0))
            elif "yellow" in content or "желт" in content or "жёлт" in content:
                color = random.random()
                ctx.set_source_rgba(color, color, 0)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(color, color, 0))
            elif "purple" in content or "фиолет" in content:
                color = random.random()
                ctx.set_source_rgba(color, 0, color)
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(color, 0, color))
            elif "no" in content or "without" in content or "без" in content:
                polygon = [voronoi_vertices[p] for p in region]
                Polygon(ctx).of_points(polygon).stroke(line_width=2)
            else:
                ctx.set_source_rgba(random.random(), random.random(), random.random())
                ctx.fill()
                Polygon(ctx).of_points(polygon).stroke(line_width=line,
                                                       pattern=Color(random.random(), random.random(), random.random()))


def make_hash(name):
    # создание названия картинки под определённый пост

    hash_object = hashlib.md5(name.encode())
    hash_string = hash_object.hexdigest()[-8::]
    return hash_string


def save_pic(name):
    image = "static/img/" + name + ".png"
    make_image(image, draw, SIZE, SIZE)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(user_id):
    # редактирование поста

    post_content = get_post(user_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Заголовок сообщения обязателен!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE post SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post_content)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(user_id):
    # удаление поста

    post_content = get_post(user_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM post WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('"{}" успешно удалено!'.format(post_content['title']))
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # вход пользователя в аккаунт
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    logout_user()
    print("Logged out")
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM post WHERE username = ?', (username,)).fetchall()
    conn.close()
    return render_template('user.html', posts=posts, user=username,
                           len_posts=len(posts))


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    # регистрация пользователя

    print("Reg")
    form = RegForm()
    if form.validate_on_submit():
        user = form.username.data
        email = form.email.data
        psw = form.password.data
        u = User(username=user, email=email)
        u.set_password(psw)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('reg.html', title='Регистрация', form=form)


if __name__ == '__main__':
    print("Starting server...")
    app.run(port=5000, host='127.0.0.1')
