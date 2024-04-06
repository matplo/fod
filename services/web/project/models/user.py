# user.py
from flask_login import UserMixin
from project import db
from werkzeug.security import check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)  # new line
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, username, email, password_hash, active):  # updated line
        self.username = username  # new line
        self.email = email
        # self.password_hash = generate_password_hash(password)
        # we assume password is stored as hashed password
        self.password_hash = password_hash
        self.active = active

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
