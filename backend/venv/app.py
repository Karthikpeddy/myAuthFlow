from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['JWT_SECRET_KEY'] = 'dev-change-this'   # use env var in prod
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg':'User already exists'}), 400
    u = User(email=data['email'], password_hash=generate_password_hash(data['password']))
    db.session.add(u); db.session.commit()
    return jsonify({'msg':'created'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = User.query.filter_by(email=data['email']).first()
    if not u or not check_password_hash(u.password_hash, data['password']):
        return jsonify({'msg':'bad credentials'}), 401
    access = create_access_token(identity=u.id)
    return jsonify({'access_token': access})

@app.route('/api/me')
@jwt_required()
def me():
    uid = get_jwt_identity()
    u = User.query.get(uid)
    return jsonify({'email': u.email})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
