from flask import Flask, request, jsonify
import os
import jwt
import datetime


app = Flask(__name__)
SECRET = os.getenv('JWT_SECRET', 'supersecret123')
ALGO = os.getenv('JWT_ALGORITHM', 'HS256')
EXP_SECONDS = int(os.getenv('JWT_EXP_SECONDS', '3600'))


# simple in-memory user store: username -> {id, username, password}
USERS = {}
NEXT_ID = 1


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

    USERS[username] = {
        "id": NEXT_ID,
        "username": username,
        "password": password
    }
    NEXT_ID += 1
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    user = USERS.get(username)
    if not user or user.get('password') != password:
        return jsonify({'error': 'invalid credentials'}), 401
    payload = {
    'sub': user['id'],
    'username': username,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=EXP_SECONDS)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGO)
    # pyjwt v2 returns str; if bytes convert
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return jsonify({'access_token': token}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('AUTH_PORT', 5000)), debug=True)