"""
WSGI entry point for homeCloud application.
This file is used by WSGI servers like gunicorn, waitress, uWSGI, etc.
"""

import os
from app import create_app

# Create application instance
application = create_app(os.getenv('FLASK_ENV', 'default'))

# For compatibility with some WSGI servers
app = application

if __name__ == "__main__":
    # This allows running the file directly for testing
    application.run(debug=application.config['DEBUG'])
