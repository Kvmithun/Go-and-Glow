import json

with open('user.json', 'r') as f:
    users = json.load(f)

new_users = {}

for email, data in users.items():
    # data is a list: [name, password]
    new_users[email] = {
        "name": data[0],
        "password": data[1],
        "reset_token": None
    }

with open('user.json', 'w') as f:
    json.dump(new_users, f, indent=4)

print("Migration complete: user.json updated to dict format.")
