import os
from flask import Flask, render_template, jsonify

def create_app():
    # Helper to find resources when run from PyInstaller
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['SECRET_KEY'] = 'dev_secret_key_change_me'

    # Register Blueprint / Routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app

import sys
