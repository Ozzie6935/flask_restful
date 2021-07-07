from flask import Flask
from webapp.blueprints.api import api_bp
from webapp.extensions import db
import os


def create_app():
    app = Flask(__name__)

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/osmanghani/venv/flaskresful/db.db'
    pwd = os.getcwd()
    dbfile = os.path.join(pwd, "db.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbfile}'
    app.config['SECRET_KEY'] = 'thisissecret'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(api_bp)
    extensions(app)

    return app

def extensions(app):
    db.init_app(app)
    return None
