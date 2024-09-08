import sqlite3
from flask import g

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