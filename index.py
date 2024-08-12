from flask import Flask, request, jsonify
import json
import os
import hashlib

app = Flask(__name__)
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

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users = load_users()

    if data['username'] in users:
        return jsonify({'error': 'Username already exists!'}), 400

    user_data = {
        'fullname': data['fullname'],
        'password': hash_password(data['password']),
        'email': data['email'],
        'school': data['school'],
        'class': data['class'],
        'phone': data['phone'],
        'address': data['address']
    }

    users[data['username']] = user_data
    save_users(users)

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()

    if data['username'] not in users or users[data['username']]['password'] != hash_password(data['password']):
        return jsonify({'error': 'Invalid username or password!'}), 400

    return jsonify({'message': 'Login successful!'}), 200

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    users = load_users()

    for username, user_data in users.items():
        if user_data['email'] == data['email'] or user_data['phone'] == data['phone']:
            new_password = hash_password(data['new_password'])
            users[username]['password'] = new_password
            save_users(users)
            return jsonify({'message': 'Password reset successfully!'}), 200

    return jsonify({'error': 'No user found with the provided email or phone number!'}), 400

@app.route('/update-info', methods=['POST'])
def update_info():
    data = request.json
    users = load_users()

    if data['username'] not in users or users[data['username']]['password'] != hash_password(data['password']):
        return jsonify({'error': 'Invalid username or password!'}), 400

    if 'fullname' in data:
        users[data['username']]['fullname'] = data['fullname']
    if 'email' in data:
        users[data['username']]['email'] = data['email']
    if 'school' in data:
        users[data['username']]['school'] = data['school']
    if 'class' in data:
        users[data['username']]['class'] = data['class']
    if 'phone' in data:
        users[data['username']]['phone'] = data['phone']
    if 'address' in data:
        users[data['username']]['address'] = data['address']
    if 'new_password' in data:
        users[data['username']]['password'] = hash_password(data['new_password'])

    save_users(users)

    return jsonify({'message': 'User info updated successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
