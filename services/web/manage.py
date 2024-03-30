import yaml
from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash

from project import app, db, User
import os

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    # get path of the current file
    current_file_path = os.path.abspath(__file__)
    users_file = os.path.join(os.path.dirname(current_file_path), 'users.yaml')
    with open(users_file, 'r') as f:
        users_list = yaml.safe_load(f)
    for user in users_list:
        # hashed_password = generate_password_hash(user['password'])
        # db.session.add(User(username=user['username'], email=user['email'], password_hash=hashed_password))
        # we assume the passwords are stored as hashed passwords
        try:
            db.session.add(User(username=user['username'], email=user['email'], password_hash=user['password_hash'], active=True))
        except Exception as e:
            print(f"Error adding user {user['username']}: {e}")
    db.session.commit()


if __name__ == "__main__":
    cli()
