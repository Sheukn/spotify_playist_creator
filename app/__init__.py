from flask import Flask
from .extensions import socketio
from .routes import main as main_blueprint

def create_app():
    app = Flask(__name__)

    # Load configurations (you can add config classes or files)
    app.config.from_pyfile('config.py')

    # Register blueprints
    app.register_blueprint(main_blueprint)

    # Initialize extensions
    socketio.init_app(app)

    return app
