from flask import Flask
from .models import db, bcrypt
from .routes import api

def create_app():
    app = Flask(__name__)

    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    api.init_app(app)

    # Initialize database
    with app.app_context():
        db.create_all()

    return app