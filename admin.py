"""
Admin routes module for homeCloud application.
Contains administrative routes for user management, folder management, and system configuration.
"""

import os
import json
import io
import base64
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import qrcode
from qrcode.image.pil import PilImage

from scripts.db import get_all_shares, create_admin_user, get_user_by_username, check_admin_exists, get_share, add_share, add_file, get_share_files, delete_share_files, delete_share
from helpers import calculate_md5, get_folder_size, format_size, _

from scripts.mimetypes import getmimeType
from helpers import calculate_md5

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


@admin_bp.route('/admin/file-manager')
def admin_file_manager():
    """
    Display the admin file manager page.
    Requires admin authentication.

    Returns:
        Admin file manager template or redirect to login
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    return render_template('admin_file_manager.html')


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

        for root, dirs, files in os.walk(abs_path):
            for file in files:
                absolute_path = os.path.join(root, file)
                md5_path = calculate_md5(absolute_path)
                extension = absolute_path.split('.')[-1]
                mimeType = getmimeType(extension)
                add_file(current_app, md5, md5_path, absolute_path, mimeType)
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

    return {'success': True}


@admin_bp.route('/admin/check-integrity/<share_md5>')
def check_share_integrity(share_md5):
    """
    Check integrity of a specific share.
    Compares files in database with files on disk.

    Args:
        share_md5 (str): MD5 hash of the share to check

    Returns:
        JSON response with integrity check results
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'not authorized'}, 401

    share = get_share(current_app, share_md5)
    if not share:
        return {'success': False, 'error': 'share not found'}, 404

    share_path = share['path']
    if not os.path.exists(share_path):
        return {'success': False, 'error': 'share path does not exist'}, 404

    # Get files from database
    db_files = get_share_files(current_app, share_md5)
    db_file_paths = {file['path'] for file in db_files}

    # Get files from disk (only direct files, no subdirectories)
    disk_files = set()
    try:
        for entry in os.scandir(share_path):
            if entry.is_file():
                disk_files.add(entry.path)
    except PermissionError:
        return {'success': False, 'error': 'permission denied'}, 403

    # Calculate differences
    missing_files = db_file_paths - disk_files  # In DB but not on disk
    extra_files = disk_files - db_file_paths    # On disk but not in DB

    result = {
        'success': True,
        'share_path': share_path,
        'files_in_db': len(db_file_paths),
        'files_on_disk': len(disk_files),
        'missing_files': len(missing_files),
        'extra_files': len(extra_files),
        'missing_file_list': list(missing_files),
        'extra_file_list': list(extra_files),
        'is_ok': len(missing_files) == 0 and len(extra_files) == 0
    }

    return result


@admin_bp.route('/admin/reindex/<share_md5>', methods=['POST'])
def reindex_share(share_md5):
    """
    Reindex a specific share.
    Updates database to match current files on disk.

    Args:
        share_md5 (str): MD5 hash of the share to reindex

    Returns:
        JSON response with reindex results
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'not authorized'}, 401

    share = get_share(current_app, share_md5)
    if not share:
        return {'success': False, 'error': 'share not found'}, 404

    share_path = share['path']
    if not os.path.exists(share_path):
        return {'success': False, 'error': 'share path does not exist'}, 404

    try:
        # Get current files from database
        old_files = get_share_files(current_app, share_md5)
        old_count = len(old_files)

        # Clear all files for this share
        delete_share_files(current_app, share_md5)

        # Re-add all files from disk (only direct files, no subdirectories)
        new_count = 0
        for entry in os.scandir(share_path):
            if entry.is_file():
                absolute_path = entry.path
                md5_path = calculate_md5(absolute_path)
                extension = absolute_path.split('.')[-1] if '.' in absolute_path else ''
                mimeType = getmimeType(extension)
                add_file(current_app, share_md5, md5_path, absolute_path, mimeType)
                new_count += 1

        result = {
            'success': True,
            'share_path': share_path,
            'files_removed': old_count,
            'files_added': new_count
        }

        return result

    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


@admin_bp.route('/admin/check-all-integrity')
def check_all_integrity():
    """
    Check integrity of all shares.
    Returns summary of integrity check for all shares.

    Returns:
        JSON response with integrity check results for all shares
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'not authorized'}, 401

    shares = get_all_shares(current_app)
    results = []
    total_missing = 0
    total_extra = 0

    for share in shares:
        share_md5 = share['md5']
        share_path = share['path']

        if not os.path.exists(share_path):
            results.append({
                'md5': share_md5,
                'path': share_path,
                'error': 'path does not exist',
                'is_ok': False
            })
            continue

        try:
            # Get files from database
            db_files = get_share_files(current_app, share_md5)
            db_file_paths = {file['path'] for file in db_files}

            # Get files from disk (only direct files, no subdirectories)
            disk_files = set()
            for entry in os.scandir(share_path):
                if entry.is_file():
                    disk_files.add(entry.path)

            # Calculate differences
            missing_files = db_file_paths - disk_files
            extra_files = disk_files - db_file_paths

            total_missing += len(missing_files)
            total_extra += len(extra_files)

            results.append({
                'md5': share_md5,
                'path': share_path,
                'files_in_db': len(db_file_paths),
                'files_on_disk': len(disk_files),
                'missing_files': len(missing_files),
                'extra_files': len(extra_files),
                'is_ok': len(missing_files) == 0 and len(extra_files) == 0
            })

        except PermissionError:
            results.append({
                'md5': share_md5,
                'path': share_path,
                'error': 'permission denied',
                'is_ok': False
            })

    return {
        'success': True,
        'total_shares': len(shares),
        'total_missing_files': total_missing,
        'total_extra_files': total_extra,
        'all_ok': total_missing == 0 and total_extra == 0,
        'shares': results
    }


@admin_bp.route('/admin/reindex-all', methods=['POST'])
def reindex_all():
    """
    Reindex all shares.
    Updates database to match current files on disk for all shares.

    Returns:
        JSON response with reindex results for all shares
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'not authorized'}, 401

    shares = get_all_shares(current_app)
    results = []
    total_removed = 0
    total_added = 0

    for share in shares:
        share_md5 = share['md5']
        share_path = share['path']

        if not os.path.exists(share_path):
            results.append({
                'md5': share_md5,
                'path': share_path,
                'error': 'path does not exist',
                'success': False
            })
            continue

        try:
            # Get current files from database
            old_files = get_share_files(current_app, share_md5)
            old_count = len(old_files)

            # Clear all files for this share
            delete_share_files(current_app, share_md5)

            # Re-add all files from disk (only direct files, no subdirectories)
            new_count = 0
            for entry in os.scandir(share_path):
                if entry.is_file():
                    absolute_path = entry.path
                    md5_path = calculate_md5(absolute_path)
                    extension = absolute_path.split('.')[-1] if '.' in absolute_path else ''
                    mimeType = getmimeType(extension)
                    add_file(current_app, share_md5, md5_path, absolute_path, mimeType)
                    new_count += 1

            total_removed += old_count
            total_added += new_count

            results.append({
                'md5': share_md5,
                'path': share_path,
                'files_removed': old_count,
                'files_added': new_count,
                'success': True
            })

        except Exception as e:
            results.append({
                'md5': share_md5,
                'path': share_path,
                'error': str(e),
                'success': False
            })

    return {
        'success': True,
        'total_shares': len(shares),
        'total_files_removed': total_removed,
        'total_files_added': total_added,
        'shares': results
    }


@admin_bp.route('/admin/delete-share/<share_md5>', methods=['DELETE'])
def delete_share_route(share_md5):
    """
    Delete a share and all its associated files from the database.

    Args:
        share_md5 (str): MD5 hash of the share to delete

    Returns:
        JSON response with success status
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'Unauthorized'}, 401

    try:
        # Check if share exists
        share = get_share(current_app, share_md5)
        if not share:
            return {'success': False, 'error': 'Share not found'}, 404

        # Delete the share and all associated files
        delete_share(current_app, share_md5)

        return {'success': True, 'message': 'Share deleted successfully'}

    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@admin_bp.route('/admin/share/externalLink/<md5_share>')
def get_external_link(md5_share):
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    external_url = current_app.config.get('EXTERNAL_URL')
    if external_url:
        base_url = external_url.rstrip('/')
    else:
        base_url = request.url_root.rstrip('/')

    share_url = f"{base_url}/share/{md5_share}"

    return jsonify({
        'success': True,
        'share_url': share_url
    })

@admin_bp.route('/admin/share/qr/<md5_share>')
def generate_admin_qr_code(md5_share):
    """
    Generate QR code for a share URL (admin version).

    Args:
        md5_share (str): MD5 hash of the share

    Returns:
        JSON response with base64 encoded QR code image
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'Unauthorized'}, 401

    try:
        # Get the base URL from config or request
        external_url = current_app.config.get('EXTERNAL_URL')
        if external_url:
            base_url = external_url.rstrip('/')
        else:
            base_url = request.url_root.rstrip('/')

        share_url = f"{base_url}/share/{md5_share}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        return jsonify({
            'success': True,
            'qr_code': f"data:image/png;base64,{img_base64}",
            'share_url': share_url
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/admin/create-folder', methods=['POST'])
def create_folder():
    """
    Create a new folder in the upload directory.

    Returns:
        JSON response with success status
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'Unauthorized'}, 401

    data = request.get_json()
    folder_name = data.get('folder_name', '').strip()
    parent_path = data.get('parent_path', '').strip()

    if not folder_name:
        return {'success': False, 'error': 'Folder name is required'}, 400

    # Secure the folder name
    folder_name = secure_filename(folder_name)
    if not folder_name:
        return {'success': False, 'error': 'Invalid folder name'}, 400

    try:
        # Build the full path
        if parent_path:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], parent_path, folder_name)
        else:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)

        # Check if folder already exists
        if os.path.exists(full_path):
            return {'success': False, 'error': 'Folder already exists'}, 400

        # Create the folder
        os.makedirs(full_path, exist_ok=True)

        return {'success': True, 'message': 'Folder created successfully', 'path': full_path}

    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


@admin_bp.route('/admin/upload-files', methods=['POST'])
def upload_files():
    """
    Upload multiple files to a specified directory.

    Returns:
        JSON response with upload results
    """
    if not session.get('admin_logged_in'):
        return {'success': False, 'error': 'Unauthorized'}, 401

    target_path = request.form.get('target_path', '').strip()

    if 'files' not in request.files:
        return {'success': False, 'error': 'No files provided'}, 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return {'success': False, 'error': 'No files selected'}, 400

    try:
        # Build target directory path
        if target_path:
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], target_path)
        else:
            upload_dir = current_app.config['UPLOAD_FOLDER']

        # Ensure target directory exists
        os.makedirs(upload_dir, exist_ok=True)

        uploaded_files = []
        failed_files = []

        for file in files:
            if file.filename == '':
                continue

            try:
                # Secure the filename
                filename = secure_filename(file.filename)
                if not filename:
                    failed_files.append({'filename': file.filename, 'error': 'Invalid filename'})
                    continue

                # Build full file path
                file_path = os.path.join(upload_dir, filename)

                # Handle duplicate filenames by adding a number
                counter = 1
                original_filename = filename
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    file_path = os.path.join(upload_dir, filename)
                    counter += 1

                # Save the file
                file.save(file_path)
                uploaded_files.append({'filename': filename, 'path': file_path})

            except Exception as e:
                failed_files.append({'filename': file.filename, 'error': str(e)})

        return {
            'success': True,
            'uploaded_files': uploaded_files,
            'failed_files': failed_files,
            'total_uploaded': len(uploaded_files),
            'total_failed': len(failed_files)
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
