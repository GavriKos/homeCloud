from flask import Flask, request, send_file, render_template, g
import sqlite3
import os, json
import hashlib

def calculate_md5(path):
    md5_hash = hashlib.md5()
    md5_hash.update(path.encode('utf-8'))
    return md5_hash.hexdigest()
    


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

@app.cli.command('db_init')
def db_init_command():
    init_db()
    print('Initialized the database.')

@app.cli.command('db_testfill')
def db_testfill_command():
    folder_path = "data\\testshare"
    share_md5 = calculate_md5(folder_path)
    add_share(share_md5, folder_path)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            absolute_path = os.path.join(root, file)
            md5_path = calculate_md5(absolute_path)
            mimeType = "unknown"
            extension = absolute_path.split('.')[-1]
            if extension == 'jpg':
                mimeType = 'image'
            if extension == 'mp4':
                mimeType = 'video'
            add_file(share_md5, md5_path, absolute_path, mimeType)
    print('Test share: ' + share_md5)

def add_share(md5, path):
    db = get_db()
    db.execute('INSERT INTO shares (md5, path) VALUES (?, ?)', (md5, path))
    db.commit()

def add_file(sharemd5, md5, path, mimeType):
    db = get_db()
    db.execute('INSERT INTO files (sharemd5, md5, path, mimetype) VALUES (?, ?, ?, ?)', (sharemd5, md5, path, mimeType))
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
        fileData = {}
        fileData["md5"] = file['md5']
        fileData["mimetype"] = file['mimetype']
        data["mediaList"].append(fileData)
    return json.dumps(data)

@app.route('/share/<md5_share>/<md5_file>')
def share(md5_share,md5_file):
    file = get_share_file(md5_share, md5_file)
    mimetype = file['mimetype']
    if mimetype == 'image':
        image_path = file['path']    
        return send_file(image_path, mimetype='image/jpeg')
    if mimetype == 'video':
        video_path = file['path']
        return send_file(video_path, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True)
