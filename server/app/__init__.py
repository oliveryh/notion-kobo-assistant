import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import create_db

app = Flask(__name__)

app.jinja_env.globals.update(
    SUBPATH=os.environ.get("SUBPATH", ""),
)

db_path = "sqlite.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_path}'
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from app import models, views

db.init_app(app)
db.create_all()
