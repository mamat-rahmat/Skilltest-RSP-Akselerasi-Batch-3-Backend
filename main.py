from datetime import datetime
from flask import Flask, json, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    full_name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Genre=Genre)

@app.post('/register')
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    full_name = request.json.get('fullName', None)
    role_name = request.json.get('role', None)
    
    if not all([email, password, full_name, role_name]):
        response = {
            "message": "Field Email, Password, FullName, Role is required!",
            "status": "bad request"
        }
        return jsonify(response), 400
    
    role = Role.query.filter_by(name=role_name).first()
    print(role_name)
    print(role)
    user = User(email=email, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    response = {
        "data": {
            "email": user.email,
            "fullName": user.full_name,
            "id": user.id,
            "role": user.role.name
        },
        "message": "Sucessfully Register!",
        "status": "success"
    }
    return jsonify(response), 200

@app.post('/signin')
def signin():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(email=email).first()

    if (user is None) or (password is None) or not(user.check_password(password)):
        response = {
            "code": 401,
            "message": "incorrect Username or Password"
        }
        return jsonify(response), 401

    response = {
        "code": 200,
        "expire": "2021-06-17T16:53:35+07:00",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MjM5MjM2MTUsImZ1bGxOYW1lIjoiU2FobGFuIEFkbWluIFhhcGllbnMiLCJpZCI6IlNhaGxhbi5OYXN1dGlvbkB4YXBpZW5zLmlkIiwib3JpZ19pYXQiOjE2MjM5MjI3MTUsInJvbGUiOiJhZG1pbiJ9.qv-npo3SnlNx32D-0o7ryLuvTEH0pGMYEOeB4sFrfTE"
    }
    return jsonify(response), 200

@app.get('/movie_reviews/user')
def get_user():
    email = request.args.get('email', None)
    user = User.query.filter_by(email=email).first()

    if user is None:
        response = {
            "errors": "record not found",
            "message": "User not found!",
            "status": "not found"
        }
        return jsonify(response), 404
    
    response = {
        "data": {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role.name
        },
        "message": "Sucessfully Get Data!",
        "status": "success"
    }
    return jsonify(response), 200

@app.put('/movie_reviews/user')
def update_user():
    email = request.args.get('email', None)
    user = User.query.filter_by(email=email).first()

    if user is None:
        response = {
            "errors": "record not found",
            "message": "User not found!",
            "status": "not found"
        }
        return jsonify(response), 404

    full_name = request.json.get('fullName', None)
    if full_name:
        user.full_name = full_name

    password = request.json.get('password', None)
    if password:
        user.set_password(password)

    db.session.add(user)
    db.session.commit()

    response = {
        "data": {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role.name
        },
        "message": "Sucessfully Get Data!",
        "status": "success"
    }
    return jsonify(response), 200
