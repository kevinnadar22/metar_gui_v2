# app/backend/__init__.py

from flask import Flask
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')


def create_app():
    app = Flask(__name__,template_folder=FRONTEND_DIR,
        static_folder=FRONTEND_DIR, 
        static_url_path='/')
    
    from .routes.api import api_bp
    from .routes.web import web

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web)

    return app
