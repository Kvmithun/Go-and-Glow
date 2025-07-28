from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from database import database
import json
import os
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
app.secret_key = 'kvmithun_secret_@123'

# ----------- File Paths -----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKINGS_FILE = os.path.join(BASE_DIR, 'bookings.json')
OWNERS_DETAILS_FILE = os.path.join(BASE_DIR, 'owners_details.json')

# ----------- Init DBs -----------
dbo = database()  # customers
dbo_owner = database("owners.json")  # owners



def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return json.load(f)
    return [] if file_path.endswith('.json') else {}


def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# ----------- Auth Routes -----------
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login')
def login():
    role = request.args.get("role")
    return render_template('login.html', messages='Login to your account', role=role)


@app.route('/register')
def register():
    role = request.args.get("role")
    return render_template('REGISTER.html', messages='Create your account', role=role)


@app.route('/perform-login', methods=['POST'])
def login_():
    email = request.form.get("user_email")
    password = request.form.get("user_password")
    role = request.form.get("role")

    if role == "owner":
        result = dbo_owner.search(email, password)
        if result:
            session['user'] = {"email": email, "role": "owner"}
            return redirect('/profile')
        return render_template('login.html', messages='Incorrect Owner Email/Password', role=role)

    result = dbo.search(email, password)
    if result:
        session['user'] = {"email": email, "role": "customer"}
        return redirect('/profile')
    return render_template('login.html', messages='Incorrect Customer Email/Password', role=role)


@app.route('/perform_register', methods=['POST'])
def register_():
    email = request.form.get("user_email")
    name = request.form.get('full_name')
    password = request.form.get("user_password")
    role = request.form.get("role")

    if role == "owner":
        if dbo_owner.insert(email, name, password):
            return render_template('login.html', messages='Owner Registration Successful, kindly Login', role=role)
        return render_template('REGISTER.html', messages='Owner Email already exists', role=role)

    if dbo.insert(email, name, password):
        return render_template('login.html', messages='Registration Successful, kindly Login', role=role)
    return render_template('REGISTER.html', messages='Email already exists', role=role)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ----------- Profile Routing -----------
@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    if user['role'] == 'owner':
        return render_template('owners_profile.html')
    elif user['role'] == 'customer':
        return render_template('profile_customer.html')
    return "Unauthorized role", 403


# ----------- Owner APIs -----------
@app.route('/get-owner-details')
def get_owner_details():
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify({})
    all_owners = load_json(OWNERS_DETAILS_FILE)
    return jsonify(all_owners.get(user['email'], {}))


@app.route('/save-owner-details', methods=['POST'])
def save_owner_details_route():
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify({"status": "error", "message": "Unauthorized"})

    data = request.get_json()
    if not data or not data.get('profilePic'):
        return jsonify({"status": "error", "message": "Missing profile data"})

    all_owners = load_json(OWNERS_DETAILS_FILE)
    all_owners[user['email']] = data
    save_json(OWNERS_DETAILS_FILE, all_owners)
    return jsonify({"status": "success"})


@app.route('/owner-appointments')
def owner_appointments():
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify([])

    bookings = load_json(BOOKINGS_FILE)
    return jsonify([b for b in bookings if b.get('owner_email') == user['email']])


# ----------- Customer APIs -----------
@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    user = session.get('user')
    if not user or user.get('role') != 'customer':
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    bookings = load_json(BOOKINGS_FILE)
    bookings.append(data)
    save_json(BOOKINGS_FILE, bookings)
    return jsonify({"status": "success"})


@app.route('/nearby-shops')
def nearby_shops():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat/lng missing"}), 400

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    all_owners = load_json(OWNERS_DETAILS_FILE)
    nearby = []

    for email, owner in all_owners.items():
        try:
            dist = haversine(lat, lng, float(owner['lat']), float(owner['lng']))
            if dist <= 50:
                o = owner.copy()
                o['email'] = email
                o['distance'] = round(dist, 2)
                nearby.append(o)
        except Exception as e:
            print(f"Error processing owner {email}: {e}")
            continue

    return jsonify(nearby)


# ----------- Optional: Customer Profile Info (for frontend) -----------
@app.route('/get-customer-profile')
def get_customer_profile():
    user = session.get('user')
    if not user or user.get('role') != 'customer':
        return jsonify({})
    return jsonify(user)


# ----------- Start Server -----------
if __name__ == '__main__':
    app.run(debug=True, port=5003)
