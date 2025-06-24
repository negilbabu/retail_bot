from flask import Flask
from .extensions import db, migrate
from .routes import api_blueprint
from .config import Config
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # initialize migrate with app and db
    from . import models
    app.register_blueprint(api_blueprint)

    return app