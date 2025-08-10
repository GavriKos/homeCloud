"""
Helper utilities module for homeCloud application.
Contains localization functions, utility methods, and common helpers.
"""

import json
import hashlib
import os
from flask import session

# --- Localization ---
with open('locales.json', encoding='utf-8') as f:
    LOCALES = json.load(f)
SUPPORTED_LANGS = ['en', 'ru']
DEFAULT_LANG = 'en'


def get_locale():
    """
    Get the current user's locale from session.
    Returns the user's selected language or default language if not set.
    
    Returns:
        str: Language code ('en' or 'ru')
    """
    lang = session.get('lang')
    if lang in SUPPORTED_LANGS:
        return lang
    return DEFAULT_LANG


def _(key):
    """
    Translate a key to the current user's language.
    
    Args:
        key (str): Translation key to look up
        
    Returns:
        str: Translated string or the key itself if translation not found
    """
    lang = get_locale()
    return LOCALES.get(lang, {}).get(key, key)


def calculate_md5(path):
    """
    Calculate MD5 hash of a file path string.
    Used for generating unique identifiers for shares and files.
    
    Args:
        path (str): File or directory path
        
    Returns:
        str: MD5 hash hexdigest of the path
    """
    md5_hash = hashlib.md5()
    md5_hash.update(path.encode('utf-8'))
    return md5_hash.hexdigest()


def get_folder_size(path):
    """
    Calculate the total size of a folder recursively.
    
    Args:
        path (str): Path to the folder
        
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_folder_size(entry.path)
    except PermissionError:
        pass
    return total_size


def format_size(size):
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"
