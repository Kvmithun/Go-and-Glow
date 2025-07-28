import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

class database:
    def __init__(self, filepath="owners.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)  # dict of users keyed by email

    def insert(self, email, name, password):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)

        if email in users:
            return 0  # Email exists

        users[email] = {
            "name": name,
            "password": generate_password_hash(password)
        }

        with open(self.filepath, 'w') as wf:
            json.dump(users, wf, indent=4)
        return 1

    def search(self, email, password):
        with open(self.filepath, 'r') as rf:
            users = json.load(rf)

        if email in users and check_password_hash(users[email]["password"], password):
            return 1
        return 0
