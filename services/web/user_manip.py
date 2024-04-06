#!/usr/bin/env python3

import yaml
import argparse
from getpass import getpass
from werkzeug.security import generate_password_hash, check_password_hash


def load_users():
    with open('users.yaml', 'r') as f:
        return yaml.safe_load(f)


def save_users(users):
    if len(users) > 0:
        with open('users.yaml', 'w') as f:
            yaml.dump(users, f)


def add_user(username, email, password, active=True):
    password_hash = generate_password_hash(password)
    new_user = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'active': active
    }

    users = load_users()
    if users:
        if username in [user['username'] for user in users]:
            print('User already exists. Use update action to change password.')
            return
    else:
        users = []
    users.append(new_user)
    save_users(users)


def delete_user(username):
    users = load_users()
    if users:
        users = [user for user in users if user['username'] != username]
        save_users(users)


def update_password(username, new_password):
    users = load_users()
    if users:
        for user in users:
            if user['username'] == username:
                user['password_hash'] = generate_password_hash(new_password)
        save_users(users)



def main():
    parser = argparse.ArgumentParser(description='Manage users.')
    parser.add_argument('action', choices=['add', 'check', 'delete', 'list', 'update'], help='The action to perform.')
    parser.add_argument('-u', '--username', help='The username of the user.')
    parser.add_argument('-e', '--email', help='The email of the user. Required for "add" action.')
    parser.add_argument('-p', '--password', help='The password of the user.')
    args = parser.parse_args()

    if args.action == 'add':
        if not args.email:
            args.email = input('Email: ')
        if not args.password:
            args.password = getpass('Password: ')
        add_user(args.username, args.email, args.password)
    elif args.action == 'check':
        if not args.password:
            args.password = getpass('Password: ')
        users = load_users()
        if users:
            for user in users:
                if user['username'] == args.username:
                    if check_password_hash(user['password_hash'], args.password):
                        print('Password is correct.')
                    else:
                        print('Password is incorrect.')
                    break
            print('User not found.')
        else:
            print('User not found.')
    elif args.action == 'list':
        # print('Listing users...')
        users = load_users()
        if users:
            for user in users:
                print(f"Username: {user['username']}, Email: {user['email']}, Active: {user['active']}")
    elif args.action == 'delete':
        delete_user(args.username)
    elif args.action == 'update':
        if not args.password:
            args.password = getpass('Password: ')
        update_password(args.username, args.password)


if __name__ == "__main__":
    main()
