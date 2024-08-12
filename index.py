from flask import Flask, request, jsonify
import hashlib
import json
import os

app = Flask(__name__)

# Đường dẫn đến file JSON
DB_FILE = 'userdb.json'

# Đọc dữ liệu từ file JSON
def read_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

# Ghi dữ liệu vào file JSON
def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Hash mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    db = read_db()

    # Kiểm tra xem email đã tồn tại hay chưa
    if data['email'] in db:
        return jsonify({'error': 'Email already registered!'}), 400

    # Thêm người dùng vào cơ sở dữ liệu
    db[data['email']] = {
        'fullname': data['fullname'],
        'password': hash_password(data['password']),
        'school': data['school'],
        'class': data['class'],
        'phone': data['phone'],
        'address': data['address']
    }
    write_db(db)

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = read_db()

    user = db.get(data['email'])

    if not user or user['password'] != hash_password(data['password']):
        return jsonify({'error': 'Invalid email or password!'}), 400

    return jsonify({'message': 'Login successful!'}), 200

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    db = read_db()

    user = db.get(data['email'])

    if not user:
        return jsonify({'error': 'No user found with the provided email!'}), 400

    # Tạo mã xác nhận tạm thời
    confirmation_code = '123456'  # Bạn có thể tạo mã xác nhận ngẫu nhiên
    db[data['email']]['confirmation_code'] = confirmation_code
    write_db(db)

    return jsonify({'message': 'Confirmation code sent (placeholder).'}), 200

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    db = read_db()

    user = db.get(data['email'])

    if not user or user.get('confirmation_code') != data['confirmation_code']:
        return jsonify({'error': 'Invalid confirmation code!'}), 400

    # Đổi mật khẩu
    db[data['email']]['password'] = hash_password(data['new_password'])
    db[data['email']].pop('confirmation_code', None)
    write_db(db)

    return jsonify({'message': 'Password reset successfully!'}), 200

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        write_db({})
    app.run(debug=True)
