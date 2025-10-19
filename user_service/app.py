from flask import Flask, request, jsonify
import os
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# === Load konfigurasi dari .env ===
load_dotenv()

app = Flask(__name__)

# Konfigurasi JWT
SECRET = os.getenv('JWT_SECRET', 'supersecret123')
ALGO = os.getenv('JWT_ALGORITHM', 'HS256')
EXP_SECONDS = int(os.getenv('JWT_EXP_SECONDS', '900'))  # default 15 menit

# In-memory user store sederhana
USERS = {}
NEXT_ID = 1


# ======================
# Endpoint: REGISTER
# ======================
@app.route("/register", methods=["POST"])
def create_user():
    global NEXT_ID
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if username in USERS:
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    USERS[username] = {
        "id": NEXT_ID,
        "username": username,
        "password": hashed_pw
    }
    NEXT_ID += 1

    return jsonify({
        "message": "User created successfully",
        "user": {"id": NEXT_ID - 1, "username": username}
    }), 201


# ======================
# Endpoint: LOGIN
# ======================
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    user = USERS.get(username)

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    payload = {
        'sub': user['id'],
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=EXP_SECONDS)
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGO)

    return jsonify({'access_token': token}), 200


# ======================
# Endpoint: VERIFY TOKEN (opsional)
# ======================
@app.route('/verify', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    try:
        decoded = jwt.decode(token, SECRET, algorithms=[ALGO])
        return jsonify({'valid': True, 'data': decoded}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


# ======================
# Jalankan server
# ======================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('AUTH_PORT', 5000)), debug=True)
