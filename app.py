# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect, url_for, abort, g, flash, make_response
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

DATABASE = '/tmp/flsite.db'
SECRET_KEY = 'roeu8u0qwo3w04h65y7o2iq'
DEBUG = True
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "авторизуйся для доступа к странице "


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


@app.errorhandler(404)
def f(error):
    return render_template("vybor.html")


@app.route('/', methods=['POST', 'GET'])
def about():
    db = get_db()
    return render_template("vybor.html")


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/login", methods=["POST", "GET"])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form.get('email'))
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False

            login_user(userlogin, remember=rm)
            session['userLogged'] = request.form['email']
            return redirect(request.args.get("next") or url_for('profile'))

    return render_template("about.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 and len(request.form['psw']) > 4:
            hpsw = generate_password_hash(request.form['psw'])
            res = dbase.addUser((request.form['name']), request.form['email'], hpsw)
            if res:
                flash("успешная регистрация")
                return redirect(url_for('login'))
            else:
                flash("ошибка")
    return render_template("register.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("ошибка обновления авы", "error")
                flash("ава обновилась")
            except FileNotFoundError as e:
                flash("ошибка чтения файла")
        else:
            flash("ошибка обновления", "error")
    return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)
