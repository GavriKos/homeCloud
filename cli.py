"""
CLI commands module for homeCloud application.
Contains Flask CLI commands for database initialization and testing.
"""

import os
import click
from flask import current_app
from flask.cli import with_appcontext

from scripts.db import add_file, add_share, init_db
from scripts.mimetypes import getmimeType
from helpers import calculate_md5


@click.command()
@with_appcontext
def db_init():
    """
    Initialize the database with required tables.
    Creates all necessary database tables for the application.
    """
    init_db(current_app)
    click.echo('Initialized the database.')


@click.command()
@with_appcontext
def db_testfill():
    """
    Fill the database with test data from the testshare folder.
    Creates a test share and adds all files from the data/testshare directory.
    """
    folder_path = "data\\testshare"
    share_md5 = calculate_md5(folder_path)
    add_share(current_app, share_md5, folder_path)
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            absolute_path = os.path.join(root, file)
            md5_path = calculate_md5(absolute_path)
            extension = absolute_path.split('.')[-1]
            mimeType = getmimeType(extension)
            add_file(current_app, share_md5, md5_path, absolute_path, mimeType)
    
    click.echo(f'Test share created: {share_md5}')


def register_cli_commands(app):
    """
    Register CLI commands with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.cli.add_command(db_init, 'db_init')
    app.cli.add_command(db_testfill, 'db_testfill')
