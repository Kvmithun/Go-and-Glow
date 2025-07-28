import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

class database:
    def __init__(self, filepath="user.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            # Initialize with empty list if file doesn't exist
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def insert(self, email, name, password):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)

        # Check if email already exists
        for user in users:
            if user.get("email") == email:
                return 0  # Duplicate email found

        # Hash the password before storing
        hashed_pw = generate_password_hash(password)

        # Append new user
        users.append({
            "email": email,
            "name": name,
            "password": hashed_pw
        })

        # Write updated users back to file
        with open(self.filepath, 'w') as wf:
            json.dump(users, wf, indent=4)
        return 1

    def search(self, email, password):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)

        # Search for matching email and password
        for user in users:
            if user.get("email") == email and check_password_hash(user.get("password"), password):
                return 1
        return 0

    def find_by_email(self, email):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)
        for user in users:
            if user.get("email") == email:
                return user
        return None

    def update(self, email, updated_user):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)

        for idx, user in enumerate(users):
            if user.get("email") == email:
                users[idx] = updated_user
                with open(self.filepath, 'w') as wf:
                    json.dump(users, wf, indent=4)
                return 1
        return 0
