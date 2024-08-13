from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import hashlib

app = Flask(__name__)

# Cấu hình kết nối đến PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://default:lIPLH31uZbeU@ep-rough-scene-a437vp78.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Định nghĩa mô hình người dùng
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    confirmation_code = db.Column(db.String(6), nullable=True)

# Hàm khởi tạo cơ sở dữ liệu
def init_db():
    with app.app_context():
        db.create_all()

# Hash mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        new_user = User(
            email=data['email'],
            fullname=data['fullname'],
            password=hash_password(data['password']),
            school=data['school'],
            class_name=data['class'],
            phone=data['phone'],
            address=data['address']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already registered!'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.password == hash_password(data['password']):
        return jsonify({'message': 'Login successful!'}), 200
    return jsonify({'error': 'Invalid email or password!'}), 400

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user:
        # Tạo mã xác nhận tạm thời
        confirmation_code = '123456'  # Bạn có thể tạo mã xác nhận ngẫu nhiên
        user.confirmation_code = confirmation_code
        db.session.commit()
        return jsonify({'message': 'Confirmation code sent (placeholder).'}), 200

    return jsonify({'error': 'No user found with the provided email!'}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.confirmation_code == data['confirmation_code']:
        user.password = hash_password(data['new_password'])
        user.confirmation_code = None
        db.session.commit()
        return jsonify({'message': 'Password reset successfully!'}), 200

    return jsonify({'error': 'Invalid confirmation code!'}), 400

@app.route('/delete-account', methods=['DELETE'])
def delete_account():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.password == hash_password(data['password']):
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully!'}), 200

    return jsonify({'error': 'Invalid email or password!'}), 400

@app.route('/update-profile', methods=['PUT'])
def update_profile():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.password == hash_password(data['password']):
        user.fullname = data.get('fullname', user.fullname)
        user.school = data.get('school', user.school)
        user.class_name = data.get('class', user.class_name)
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200

    return jsonify({'error': 'Invalid email or password!'}), 400

@app.route('/change-password', methods=['PUT'])
def change_password():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and user.password == hash_password(data['current_password']):
        user.password = hash_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully!'}), 200

    return jsonify({'error': 'Invalid email or current password!'}), 400

if __name__ == '__main__':
    init_db()  # Khởi tạo cơ sở dữ liệu khi ứng dụng bắt đầu
    app.run(debug=True)
