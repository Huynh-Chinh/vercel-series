from flask import Flask, request, jsonify
import json
import os
import hashlib
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)

# Cấu hình email (thay đổi thông tin dưới đây với cấu hình email của bạn)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)
db_file = 'userdb.json'

def load_users():
    if not os.path.exists(db_file):
        return {}
    with open(db_file, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(db_file, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users = load_users()

    if data['email'] in users:
        return jsonify({'error': 'Email already registered!'}), 400

    confirmation_code = generate_confirmation_code()
    users[data['email']] = {
        'fullname': data['fullname'],
        'password': hash_password(data['password']),
        'email': data['email'],
        'school': data['school'],
        'class': data['class'],
        'phone': data['phone'],
        'address': data['address'],
        'confirmation_code': confirmation_code,
        'is_confirmed': False
    }
    save_users(users)

    # Gửi email xác nhận
    msg = Message('Your confirmation code', sender='your_email@gmail.com', recipients=[data['email']])
    msg.body = f'Your confirmation code is: {confirmation_code}'
    mail.send(msg)

    return jsonify({'message': 'User registered successfully! Please check your email for the confirmation code.'}), 201

@app.route('/confirm-registration', methods=['POST'])
def confirm_registration():
    data = request.json
    users = load_users()

    user = users.get(data['email'])
    if user and user['confirmation_code'] == data['confirmation_code']:
        user['is_confirmed'] = True
        save_users(users)
        return jsonify({'message': 'User confirmed successfully!'}), 200

    return jsonify({'error': 'Invalid confirmation code or email!'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()

    user = users.get(data['email'])
    if not user:
        return jsonify({'error': 'Email not found!'}), 400
    if not user['is_confirmed']:
        return jsonify({'error': 'Email not confirmed! Please check your email for the confirmation code.'}), 400
    if user['password'] != hash_password(data['password']):
        return jsonify({'error': 'Invalid password!'}), 400

    return jsonify({'message': 'Login successful!'}), 200

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    users = load_users()

    user = users.get(data['email'])
    if user:
        confirmation_code = generate_confirmation_code()
        user['confirmation_code'] = confirmation_code
        save_users(users)

        # Gửi email xác nhận
        msg = Message('Password reset confirmation code', sender='your_email@gmail.com', recipients=[data['email']])
        msg.body = f'Your password reset confirmation code is: {confirmation_code}'
        mail.send(msg)

        return jsonify({'message': 'Password reset code sent to your email!'}), 200

    return jsonify({'error': 'Email not found!'}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    users = load_users()

    user = users.get(data['email'])
    if user and user['confirmation_code'] == data['confirmation_code']:
        user['password'] = hash_password(data['new_password'])
        save_users(users)
        return jsonify({'message': 'Password reset successfully!'}), 200

    return jsonify({'error': 'Invalid confirmation code or email!'}), 400

if __name__ == '__main__':
    app.run(debug=True)
