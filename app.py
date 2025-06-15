from flask import Flask, g, request, send_file, render_template, redirect, url_for, session, flash
import os
import json
import hashlib
from scripts.db import add_file, add_share, get_share_file, get_share_files, init_db, get_all_shares, create_admin_user, get_user_by_username, check_admin_exists
from scripts.mimetypes import getFileByMimetype, getmimeType
from config import config


def calculate_md5(path):
    md5_hash = hashlib.md5()
    md5_hash.update(path.encode('utf-8'))
    return md5_hash.hexdigest()


def create_app(config_name='default'):
    app = Flask(__name__)
    # Загружаем конфигурацию
    app.config.from_object(config[config_name])
    app.secret_key = 'your_secret_key_here'  # Замените на свой секретный ключ

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


    @app.route('/')
    def index():
        admin_exists = check_admin_exists(app)
        if not admin_exists:
            return render_template('index.html')
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return redirect(url_for('admin'))


    @app.route('/share/<md5>')
    def getShare(md5):
        return render_template('share_view.html')


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


    @app.route('/register_admin', methods=['GET', 'POST'])
    def register_admin():
        if check_admin_exists(app):
            return redirect(url_for('login'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            create_admin_user(app, username, password)
            flash('Админ создан. Войдите.')
            return redirect(url_for('login'))
        return render_template('register_admin.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if not check_admin_exists(app):
            return redirect(url_for('register_admin'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = get_user_by_username(app, username)
            if user and user['is_admin'] == 1:
                from werkzeug.security import check_password_hash
                if check_password_hash(user['password_hash'], password):
                    session['admin_logged_in'] = True
                    return redirect(url_for('admin'))
            flash('Неверный логин или пароль')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('admin_logged_in', None)
        return redirect(url_for('login'))

    @app.route('/admin')
    def admin():
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        shares = get_all_shares(app)
        return render_template('admin.html', shares=shares)
    
    @app.route('/config-check')
    def config_check():
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        
        config_info = {
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'DATABASE': app.config['DATABASE'],
            'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER'],
            'DEBUG': app.config['DEBUG'],
            'SECRET_KEY_SET': bool(app.config['SECRET_KEY'] != 'dev')
        }
        return json.dumps(config_info, indent=2)

    return app

# Создаем приложение с нужной конфигурацией
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=True)
