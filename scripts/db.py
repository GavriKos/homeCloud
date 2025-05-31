import sqlite3
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

def get_db(app):
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db(app):
    db = get_db(app)
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def add_share(app, md5, path):
    db = get_db(app)
    db.execute('INSERT INTO shares (md5, path) VALUES (?, ?)', (md5, path))
    db.commit()


def add_file(app, sharemd5, md5, path, mimeType):
    db = get_db(app)
    db.execute('INSERT INTO files (sharemd5, md5, path, mimetype) VALUES (?, ?, ?, ?)',
               (sharemd5, md5, path, mimeType))
    db.commit()


def get_share(app, md5):
    db = get_db(app)
    share = db.execute('SELECT * FROM shares WHERE md5 = ?', (md5,)).fetchone()
    return share


def get_share_files(app, sharemd5):
    db = get_db(app)
    share = db.execute(
        'SELECT * FROM files WHERE sharemd5 = ?', (sharemd5,)).fetchall()
    return share


def get_share_file(app, sharemd5, md5):
    db = get_db(app)
    share = db.execute(
        'SELECT * FROM files WHERE sharemd5 = ? AND md5 = ?', (sharemd5, md5,)).fetchone()
    return share


def get_all_shares(app):
    db = get_db(app)
    shares = db.execute('SELECT * FROM shares').fetchall()
    return shares

def create_admin_user(app, username, password):
    db = get_db(app)
    password_hash = generate_password_hash(password)
    db.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)', (username, password_hash))
    db.commit()

def get_user_by_username(app, username):
    db = get_db(app)
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user

def check_admin_exists(app):
    db = get_db(app)
    user = db.execute('SELECT * FROM users WHERE is_admin = 1').fetchone()
    return user is not None