from flask import Flask, request, jsonify
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


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

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