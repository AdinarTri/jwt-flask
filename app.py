from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# Menggunakan environment variable untuk secret key jika ada, jika tidak pakai default
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "rivaldo_100") 
jwt = JWTManager(app)

users = {
    "user1": {
        "password": generate_password_hash("password123"), 
        "profile": {
            "name": "Aleks",
            "email": "pertamina@example.com",
            "role": "user"
        }
    },
    "admin1": {
        "password": generate_password_hash("adminpass123"),
        "profile": {
            "name": "Bob",
            "email": "bob@example.com",
            "role": "admin"
        }
    }
}

# --- API Endpoints ---

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    username = data.get("username", None)
    password = data.get("password", None)

    user = users.get(username, None)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_username = get_jwt_identity()
    user = users.get(current_user_username, None)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(logged_in_as=current_user_username, profile=user["profile"]), 200

# --- Frontend Routes ---

@app.route("/")
def home():
    """Menampilkan halaman utama (dashboard UI)."""
    return render_template("dashboard.html")

# Memastikan blok ini berjalan dengan benar
if __name__ == "__main__":
    # Membuat folder templates jika belum ada
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5001)