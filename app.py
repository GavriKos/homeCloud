from flask import Flask, g, request, render_template, redirect, url_for, session, make_response
import os
from config import config

from helpers import get_locale, _, SUPPORTED_LANGS, DEFAULT_LANG
from admin import admin_bp
from guest import guest_bp
from cli import register_cli_commands
from scripts.db import check_admin_exists

def create_app(config_name='default'):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): Configuration name to use ('default', 'development', 'production')

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Make translation function available in all templates
    @app.context_processor
    def inject_translator():
        """
        Inject translation functions into template context.

        Returns:
            dict: Dictionary with translation functions
        """
        return {'_': _, 'get_locale': get_locale}

    @app.route('/set-lang/<lang>')
    def set_lang(lang):
        """
        Set user's language preference in session.

        Args:
            lang (str): Language code to set

        Returns:
            Response: Redirect to referrer or index page
        """
        if lang not in SUPPORTED_LANGS:
            lang = DEFAULT_LANG
        session['lang'] = lang
        resp = make_response(redirect(request.referrer or url_for('index')))
        return resp

    @app.teardown_appcontext
    def close_db(error):
        """
        Close database connection when application context tears down.

        Args:
            error: Any error that occurred during request processing
        """
        if 'db' in g:
            g.db.close()




    @app.route('/')
    def index():
        """
        Main index route that redirects based on admin status and authentication.

        Returns:
            Response: Rendered template or redirect based on conditions
        """
        admin_exists = check_admin_exists(app)
        if not admin_exists:
            return render_template('index.html')
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return redirect(url_for('admin.admin_folders'))

    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(guest_bp)

    # Register CLI commands
    register_cli_commands(app)

    return app

# Создаем приложение с нужной конфигурацией
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
