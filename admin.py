"""
Admin routes module for homeCloud application.
Contains administrative routes for user management, folder management, and system configuration.
"""

import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash

from scripts.db import get_all_shares, create_admin_user, get_user_by_username, check_admin_exists, get_share, add_share
from helpers import calculate_md5, get_folder_size, format_size, _

# Create blueprint for admin routes
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    """
    Register the first admin user for the system.
    Only accessible when no admin exists yet.
    
    Returns:
        Registration form or redirect to login after successful registration
    """
    if check_admin_exists(current_app):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_admin_user(current_app, username, password)
        flash(_('admin_created_please_login'))
        return redirect(url_for('admin.login'))
    
    return render_template('register_admin.html')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin login page and authentication handler.
    Validates admin credentials and creates session.

    Returns:
        Login form or redirect to admin panel after successful login
    """
    if not check_admin_exists(current_app):
        return redirect(url_for('admin.register_admin'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(current_app, username)

        if user and user['is_admin'] == 1:
            if check_password_hash(user['password_hash'], password):
                session['admin_logged_in'] = True
                return redirect(url_for('admin.admin_folders'))

        flash(_('invalid_login_or_password'))

    return render_template('login.html')


@admin_bp.route('/logout')
def logout():
    """
    Log out the admin user by clearing the session.

    Returns:
        Redirect to login page
    """
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/admin')
def admin_redirect():
    """
    Redirect admin root to folders page.

    Returns:
        Redirect to admin folders page
    """
    return redirect(url_for('admin.admin_folders'))


@admin_bp.route('/admin/folders')
def admin_folders():
    """
    Display the admin folders management page.
    Requires admin authentication.

    Returns:
        Admin folders template or redirect to login
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    return render_template('admin_folders.html')


@admin_bp.route('/admin/shares')
def admin_shares():
    """
    Display all existing shares in the admin panel.
    Shows a list of all created shares with their details.

    Returns:
        Admin shares template with shares data or redirect to login
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    shares = get_all_shares(current_app)
    return render_template('admin_shares.html', shares=shares)


@admin_bp.route('/admin/config-check')
def config_check():
    """
    Display current application configuration for debugging.
    Shows environment variables and config settings.

    Returns:
        JSON response with configuration information or redirect to login
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    config_info = {
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'DATABASE': current_app.config['DATABASE'],
        'UPLOAD_FOLDER': current_app.config['UPLOAD_FOLDER'],
        'DEBUG': current_app.config['DEBUG'],
        'SECRET_KEY_SET': bool(current_app.config['SECRET_KEY'] != 'dev')
    }
    return json.dumps(config_info, indent=2)


@admin_bp.route('/admin/folder-tree')
def admin_folder_tree():
    """
    Get folder tree structure as JSON for the admin interface.
    Recursively scans the upload folder and returns folder hierarchy with sizes.

    Returns:
        JSON response with folder tree structure or redirect to login
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    def get_folder_tree(path):
        """
        Recursively build folder tree structure.

        Args:
            path (str): Path to scan

        Returns:
            list: List of folder dictionaries with metadata
        """
        tree = []
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    subtree = get_folder_tree(entry.path)
                    folder_size = get_folder_size(entry.path)
                    rel_path = os.path.relpath(entry.path, current_app.config['UPLOAD_FOLDER'])
                    md5 = calculate_md5(entry.path)

                    # Check if folder is already shared
                    is_shared = get_share(current_app, md5) is not None

                    tree.append({
                        'name': entry.name,
                        'path': rel_path,
                        'size': format_size(folder_size),
                        'size_bytes': folder_size,
                        'is_shared': is_shared,
                        'md5': md5,
                        'children': subtree
                    })
        except PermissionError:
            pass
        return tree

    root = current_app.config['UPLOAD_FOLDER']
    return json.dumps(get_folder_tree(root), ensure_ascii=False)


@admin_bp.route('/admin/share-folder', methods=['POST'])
def share_folder():
    """
    Create a new share for a folder.
    Accepts JSON data with folder path and creates a share entry.

    Returns:
        JSON response with success status or error message
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'not authorized'}, 401

    data = request.get_json()
    rel_path = data.get('path')

    if not rel_path:
        return {'success': False, 'error': 'no path provided'}, 400

    abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], rel_path)

    if not os.path.isdir(abs_path):
        return {'success': False, 'error': 'not a directory'}, 400

    md5 = calculate_md5(abs_path)

    try:
        add_share(current_app, md5, abs_path)
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

    return {'success': True}
