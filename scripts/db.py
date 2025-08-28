"""
Database operations module for homeCloud application.
Contains functions for database initialization and data manipulation.
"""

import sqlite3
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash


def get_db(app):
    """
    Get database connection from Flask application context.

    Args:
        app: Flask application instance

    Returns:
        sqlite3.Connection: Database connection object
    """
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    """
    Initialize database with schema from schema.sql file.

    Args:
        app: Flask application instance
    """
    db = get_db(app)
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def add_share(app, md5, path):
    """
    Add a new share to the database.

    Args:
        app: Flask application instance
        md5 (str): MD5 hash of the share
        path (str): File system path to the shared folder
    """
    db = get_db(app)
    db.execute('INSERT INTO shares (md5, path) VALUES (?, ?)', (md5, path))
    db.commit()


def add_file(app, sharemd5, md5, path, mimeType):
    """
    Add a file to a share in the database.

    Args:
        app: Flask application instance
        sharemd5 (str): MD5 hash of the parent share
        md5 (str): MD5 hash of the file
        path (str): File system path to the file
        mimeType (str): MIME type of the file
    """
    db = get_db(app)
    db.execute('INSERT INTO files (sharemd5, md5, path, mimetype) VALUES (?, ?, ?, ?)',
               (sharemd5, md5, path, mimeType))
    db.commit()


def get_share(app, md5):
    """
    Get share information by MD5 hash.

    Args:
        app: Flask application instance
        md5 (str): MD5 hash of the share

    Returns:
        sqlite3.Row or None: Share record or None if not found
    """
    db = get_db(app)
    share = db.execute('SELECT * FROM shares WHERE md5 = ?', (md5,)).fetchone()
    return share


def get_share_files(app, sharemd5):
    """
    Get all files belonging to a share.

    Args:
        app: Flask application instance
        sharemd5 (str): MD5 hash of the share

    Returns:
        list: List of file records
    """
    db = get_db(app)
    share = db.execute(
        'SELECT * FROM files WHERE sharemd5 = ?', (sharemd5,)).fetchall()
    return share


def get_share_file(app, sharemd5, md5):
    """
    Get specific file from a share.

    Args:
        app: Flask application instance
        sharemd5 (str): MD5 hash of the share
        md5 (str): MD5 hash of the file

    Returns:
        sqlite3.Row or None: File record or None if not found
    """
    db = get_db(app)
    share = db.execute(
        'SELECT * FROM files WHERE sharemd5 = ? AND md5 = ?', (sharemd5, md5,)).fetchone()
    return share


def get_all_shares(app):
    """
    Get all shares from the database.

    Args:
        app: Flask application instance

    Returns:
        list: List of all share records
    """
    db = get_db(app)
    shares = db.execute('SELECT * FROM shares').fetchall()
    return shares


def create_admin_user(app, username, password):
    """
    Create a new admin user in the database.

    Args:
        app: Flask application instance
        username (str): Username for the admin
        password (str): Plain text password (will be hashed)
    """
    db = get_db(app)
    password_hash = generate_password_hash(password)
    db.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)', (username, password_hash))
    db.commit()


def get_user_by_username(app, username):
    """
    Get user information by username.

    Args:
        app: Flask application instance
        username (str): Username to search for

    Returns:
        sqlite3.Row or None: User record or None if not found
    """
    db = get_db(app)
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user


def check_admin_exists(app):
    """
    Check if any admin user exists in the database.

    Args:
        app: Flask application instance

    Returns:
        bool: True if admin exists, False otherwise
    """
    db = get_db(app)
    user = db.execute('SELECT * FROM users WHERE is_admin = 1').fetchone()
    return user is not None


def delete_share_files(app, sharemd5):
    """
    Delete all files belonging to a share from the database.

    Args:
        app: Flask application instance
        sharemd5 (str): MD5 hash of the share
    """
    db = get_db(app)
    db.execute('DELETE FROM files WHERE sharemd5 = ?', (sharemd5,))
    db.commit()


def delete_share(app, sharemd5):
    """
    Delete a share and all its files from the database.

    Args:
        app: Flask application instance
        sharemd5 (str): MD5 hash of the share
    """
    db = get_db(app)
    delete_share_files(app, sharemd5)
    db.execute('DELETE FROM shares WHERE md5 = ?', (sharemd5,))
    db.commit()