import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', os.environ.get('SECRET_KEY', 'dev-key-123'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app import models  # noqa: E402
from app import routes  # noqa: E402

with app.app_context():
    retries = 8
    while retries > 0:
        try:
            db.create_all()
            print("[facebouk] Database tables mapped.")
            break
        except OperationalError:
            retries -= 1
            print(f"[facebouk] DB not ready... ({retries} retries left)")
            time.sleep(3)
