from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from .routes.api import api_bp
    from .routes.web import web

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web)

    return app
