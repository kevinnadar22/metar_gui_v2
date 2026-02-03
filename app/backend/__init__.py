# app/backend/__init__.py

from flask import Flask
import os
from flask_cors import CORS
from .config import Config
from .models import db
from .auth import create_super_admin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')


def create_app():
    app = Flask(__name__,template_folder=FRONTEND_DIR,
        static_folder=FRONTEND_DIR, 
        static_url_path='/')
    
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)
    db.init_app(app)
    
    from .routes.api import api_bp
    from .routes.web import web
    from .auth import auth_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        db.create_all()
        create_super_admin()
    

    return app


