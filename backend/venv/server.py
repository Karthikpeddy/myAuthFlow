# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from flask_cors import CORS
# import datetime

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# app.config['JWT_SECRET_KEY'] = 'dev-change-this'   # use env var in prod
# db = SQLAlchemy(app)
# jwt = JWTManager(app)
# CORS(app, supports_credentials=True)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# @app.route('/api/signup', methods=['POST'])
# def signup():
#     data = request.json
#     if User.query.filter_by(email=data['email']).first():
#         return jsonify({'msg':'User already exists'}), 400
#     u = User(email=data['email'], password_hash=generate_password_hash(data['password']))
#     db.session.add(u); db.session.commit()
#     return jsonify({'msg':'created'}), 201

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     u = User.query.filter_by(email=data['email']).first()
#     if not u or not check_password_hash(u.password_hash, data['password']):
#         return jsonify({'msg':'bad credentials'}), 401
#     access = create_access_token(identity=u.id)
#     return jsonify({'access_token': access})

# @app.route('/api/me')
# @jwt_required()
# def me():
#     uid = get_jwt_identity()
#     u = User.query.get(uid)
#     return jsonify({'email': u.email})

# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True)


import os, json, datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dev-change-this'
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

USERS_FILE = "users.json"

# --- Helpers ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def find_user_by_email(email):
    users = load_users()
    return next((u for u in users if u["email"] == email), None)

# --- Signup ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    users = load_users()
    if find_user_by_email(data['email']):
        return jsonify({'msg':'User already exists'}), 400
    new_user = {
        "id": len(users)+1,
        "email": data['email'],
        "password_hash": generate_password_hash(data['password']),
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    users.append(new_user)
    save_users(users)
    return jsonify({'msg':'created'}), 201

# --- Login ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = find_user_by_email(data['email'])
    if not u or not check_password_hash(u['password_hash'], data['password']):
        return jsonify({'msg':'bad credentials'}), 401
    access = create_access_token(identity=u['id'], expires_delta=datetime.timedelta(hours=1))
    return jsonify({'access_token': access})

# --- Forgot Password ---
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get("email")
    u = find_user_by_email(email)
    if not u:
        return jsonify({"msg": "User not found"}), 404

    # Generate reset token valid for 15 minutes
    reset_token = create_access_token(identity=u["id"], expires_delta=datetime.timedelta(minutes=15))
    reset_link = f"http://localhost:3000/reset-password/{reset_token}"

    # Send email
    send_email(email, reset_link)
    return jsonify({"msg": "Password reset link sent"}), 200

def send_email(to_email, reset_link):
    # Example using SMTP (Gmail or other)
    EMAIL_ADDRESS = "your_email@example.com"
    EMAIL_PASSWORD = "your_email_password"

    msg = EmailMessage()
    msg['Subject'] = "Password Reset Request"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f"Click the link to reset your password:\n{reset_link}\n\nThis link is valid for 15 minutes.")

    # Use your SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# --- Reset Password ---
@app.route('/api/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.json
        decoded = decode_token(token)
        uid = decoded['sub']  # identity from token
        new_password = data.get("new_password")
        if not new_password:
            return jsonify({"msg": "Password required"}), 400

        users = load_users()
        for u in users:
            if u["id"] == uid:
                u["password_hash"] = generate_password_hash(new_password)
                save_users(users)
                return jsonify({"msg":"Password reset successful"}), 200

        return jsonify({"msg":"User not found"}), 404
    except Exception as e:
        return jsonify({"msg":"Invalid or expired token"}), 400

# --- Main ---
if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_users([])
    app.run(debug=True)

