import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import create_db

persistent_path = os.getenv("PERSISTENT_STORAGE_DIR")

app = Flask(__name__)
print(persistent_path)
db_path = os.path.join(persistent_path, "sqlite.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_path}'
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from app import models, views

db.init_app(app)
db.create_all()
