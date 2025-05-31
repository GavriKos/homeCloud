from flask import Flask, g, request, send_file, render_template
import os
import json
import hashlib
from scripts.db import add_file, add_share, get_share_file, get_share_files, init_db, get_all_shares

from scripts.mimetypes import getFileByMimetype, getmimeType


def calculate_md5(path):
    md5_hash = hashlib.md5()
    md5_hash.update(path.encode('utf-8'))
    return md5_hash.hexdigest()


app = Flask(__name__)
app.config['DATABASE'] = 'database.db'

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

@app.cli.command('db_init')
def db_init_command():
    init_db(app)
    print('Initialized the database.')


@app.cli.command('db_testfill')
def db_testfill_command():
    folder_path = "data\\testshare"
    share_md5 = calculate_md5(folder_path)
    add_share(app, share_md5, folder_path)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            absolute_path = os.path.join(root, file)
            md5_path = calculate_md5(absolute_path)
            extension = absolute_path.split('.')[-1]
            mimeType = getmimeType(extension)
            add_file(app, share_md5, md5_path, absolute_path, mimeType)
    print('Test share: ' + share_md5)


@app.route('/share/<md5>')
def getShare(md5):
    return render_template('index.html')


@app.route('/external-viewer/<mimetype>/<md5_share>/<md5_file>')
def getExternalViwer(mimetype, md5_share, md5_file):
    if mimetype == "maptrack":
        return render_template('external-viewers/map.html', share_md5=md5_share, file_md5=md5_file)


@app.route('/share/all/<md5_share>')
def getAllfromShare(md5_share):
    data = {}
    data["mediaList"] = []
    files = get_share_files(app, md5_share)
    for file in files:
        fileData = {}
        fileData["md5"] = file['md5']
        fileData["mimetype"] = file['mimetype']
        data["mediaList"].append(fileData)
    return json.dumps(data)


@app.route('/share/<md5_share>/<md5_file>')
def share(md5_share, md5_file):
    file = get_share_file(app, md5_share, md5_file)
    mimetype = file['mimetype']
    filepath = file['path']
    return getFileByMimetype(mimetype, filepath)


@app.route('/admin')
def admin():
    shares = get_all_shares(app)
    return render_template('admin.html', shares=shares)

if __name__ == '__main__':
    app.run(debug=True)
