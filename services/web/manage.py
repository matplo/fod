import yaml
from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash

from project import app, db, User
import os

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    """Create database tables if they do not exist (idempotent & safe)."""
    db.create_all()
    db.session.commit()
    print("Database tables created or verified.")


@cli.command("reset_db")
def reset_db():
    """Drop and recreate all database tables (destructive)."""
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Database dropped and recreated.")


@cli.command("seed_db")
def seed_db():
    """Sync users from users.yaml into the database without dropping existing data."""
    current_file_path = os.path.abspath(__file__)
    users_file = os.path.join(os.path.dirname(current_file_path), 'users.yaml')
    if not os.path.exists(users_file):
        print(f"Users file {users_file} does not exist.")
        return
    with open(users_file, 'r') as f:
        users_list = yaml.safe_load(f) or []
    for user in users_list:
        try:
            existing = User.query.filter_by(username=user['username']).first()
            if existing:
                existing.email = user['email']
                existing.password_hash = user['password_hash']
                existing.active = user.get('active', True)
            else:
                db.session.add(User(
                    username=user['username'],
                    email=user['email'],
                    password_hash=user['password_hash'],
                    active=user.get('active', True)
                ))
        except Exception as e:
            print(f"Error syncing user {user.get('username')}: {e}")
    # Clean up users no longer in users.yaml
    valid_usernames = {u['username'] for u in users_list}
    if not valid_usernames:
        print("No users configured in users.yaml; skipping cleanup.")
        db.session.commit()
        return
    for db_user in User.query.all():
        if db_user.username not in valid_usernames:
            db.session.delete(db_user)
    db.session.commit()
    print("Users synced successfully.")


if __name__ == "__main__":
    cli()
