from flask import Flask, request, send_file, render_template, g
import sqlite3
import os, json

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    add_share("testshare", "data/testshare")
    add_file("testshare","4","data/testshare/1.jpg")
    add_file("testshare","5","data/testshare/2.jpg")
    add_file("testshare","6","data/testshare/3.jpg")
    print('Initialized the database.')

def add_share(md5, path):
    db = get_db()
    db.execute('INSERT INTO shares (md5, path) VALUES (?, ?)', (md5, path))
    db.commit()

def add_file(sharemd5, md5, path):
    db = get_db()
    db.execute('INSERT INTO files (sharemd5, md5, path) VALUES (?, ?, ?)', (sharemd5, md5, path))
    db.commit()

def get_share(md5):
    db = get_db()
    share = db.execute('SELECT * FROM shares WHERE md5 = ?', (md5,)).fetchone()
    return share

def get_share_files(sharemd5):
    db = get_db()
    share = db.execute('SELECT * FROM files WHERE sharemd5 = ?', (sharemd5,)).fetchall()
    return share

def get_share_file(sharemd5, md5):
    db = get_db()
    share = db.execute('SELECT * FROM files WHERE sharemd5 = ? AND md5 = ?', (sharemd5,md5,)).fetchone()
    return share

@app.route('/share/<md5>')
def getShare(md5):
    return render_template('index.html')

@app.route('/share/all/<md5_share>')
def getAllfromShare(md5_share):
    data = {}
    data["mediaList"] = []
    files = get_share_files(md5_share)
    for file in files:
        data["mediaList"].append(file['md5'])
    return json.dumps(data)

@app.route('/share/<md5_share>/<md5_file>')
def share(md5_share,md5_file):
    file = get_share_file(md5_share, md5_file)
    image_path = file['path']
    
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
