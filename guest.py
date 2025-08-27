"""
Guest routes module for homeCloud application.
Contains public routes for file sharing and viewing without authentication.
"""

import json
from flask import Blueprint, render_template, current_app

from scripts.db import get_share_file, get_share_files
from scripts.mimetypes import getFileByMimetype

# Create blueprint for guest routes
guest_bp = Blueprint('guest', __name__)


@guest_bp.route('/share/<md5>')
def get_share(md5):
    """
    Display the share view page for a given share MD5.
    
    Args:
        md5 (str): MD5 hash of the share
        
    Returns:
        Rendered template for share viewing
    """
    return render_template('share_view.html')


@guest_bp.route('/external-viewer/<mimetype>/<md5_share>/<md5_file>')
def get_external_viewer(mimetype, md5_share, md5_file):
    """
    Display external viewer for specific file types.
    Currently supports map viewer for maptrack files.
    
    Args:
        mimetype (str): MIME type identifier
        md5_share (str): MD5 hash of the share
        md5_file (str): MD5 hash of the file
        
    Returns:
        Rendered template for external viewer or None
    """
    if mimetype == "maptrack":
        return render_template('external-viewers/map.html', 
                             share_md5=md5_share, 
                             file_md5=md5_file)


@guest_bp.route('/share/all/<md5_share>')
def get_all_from_share(md5_share):
    """
    Get all files from a share as JSON data.
    Returns a list of all files in the share with their metadata.
    
    Args:
        md5_share (str): MD5 hash of the share
        
    Returns:
        JSON response containing list of files with MD5 and mimetype
    """
    data = {}
    data["mediaList"] = []
    print("test1");
    files = get_share_files(current_app, md5_share)
    print("test2");
    print(files);
    
    for file in files:
        fileData = {}
        fileData["md5"] = file['md5']
        fileData["mimetype"] = file['mimetype']
        data["mediaList"].append(fileData)
    
    return json.dumps(data)


@guest_bp.route('/share/<md5_share>/<md5_file>')
def share_file(md5_share, md5_file):
    """
    Serve a specific file from a share.
    Retrieves and serves the file based on its MIME type.
    
    Args:
        md5_share (str): MD5 hash of the share
        md5_file (str): MD5 hash of the file
        
    Returns:
        File response based on MIME type
    """
    file = get_share_file(current_app, md5_share, md5_file)
    mimetype = file['mimetype']
    filepath = file['path']
    return getFileByMimetype(mimetype, filepath)
