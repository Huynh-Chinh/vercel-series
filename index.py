from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import hashlib
import random
import os

app = Flask(__name__)

# Cấu hình SQLAlchemy và Flask-Mail
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Cấu hình server SMTP, ví dụ Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'leonardo.chemistryexplorer@gmail.com'  # Thay bằng email của bạn
app.config['MAIL_PASSWORD'] = 'Leonardo.chemistry@2024'  # Thay bằng mật khẩu ứng dụng của bạn
app.config['MAIL_DEFAULT_SENDER'] = 'leonardo.chemistryexplorer@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    school = db.Column(db.String(100), nullable=True)
    user_class = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    confirmation_code = db.Column(db.String(6), nullable=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_confirmation_code():
    return str(random.randint(100000, 999999))

def send_confirmation_email(email, code):
    msg = Message('Confirmation Code', recipients=[email])
    msg.body = f'Your confirmation code is: {code}'
    mail.send(msg)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered!'}), 400

    confirmation_code = generate_confirmation_code()
    send_confirmation_email(data['email'], confirmation_code)

    new_user = User(
        fullname=data['fullname'],
        email=data['email'],
        password=hash_password(data['password']),
        school=data['school'],
        user_class=data['class'],
        phone=data['phone'],
        address=data['address'],
        confirmation_code=confirmation_code
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Confirmation code sent to your email. Please verify.'}), 201

@app.route('/confirm-registration', methods=['POST'])
def confirm_registration():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or user.confirmation_code != data['confirmation_code']:
        return jsonify({'error': 'Invalid confirmation code!'}), 400

    user.confirmation_code = None
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or user.password != hash_password(data['password']):
        return jsonify({'error': 'Invalid email or password!'}), 400

    return jsonify({'message': 'Login successful!'}), 200

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user:
        confirmation_code = generate_confirmation_code()
        send_confirmation_email(user.email, confirmation_code)
        user.confirmation_code = confirmation_code
        db.session.commit()
        return jsonify({'message': 'Confirmation code sent to your email.'}), 200

    return jsonify({'error': 'No user found with the provided email!'}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or user.confirmation_code != data['confirmation_code']:
        return jsonify({'error': 'Invalid confirmation code!'}), 400

    user.password = hash_password(data['new_password'])
    user.confirmation_code = None
    db.session.commit()

    return jsonify({'message': 'Password reset successfully!'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
