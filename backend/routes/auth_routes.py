from flask import Blueprint, request, jsonify
from app import db
from models import Role, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)

auth_bp = Blueprint('auth', __name__)

BLOCKLIST = set()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        hashed_password = generate_password_hash(data['password'])
        user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_password,
            role_id=data['role_id'],
            status=data.get('status', 'active')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.status != 'active':
            return jsonify({'error': 'User account is not active'}), 403
        if not check_password_hash(user.password, data.get('password')):
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({'message': 'Login successful', 'access_token': access_token, 'refresh_token': refresh_token, 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  
    BLOCKLIST.add(jti)
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@auth_bp.route('/roles', methods=['GET'])
def get_roles():
    try:
        roles = Role.query.all()
        return jsonify([role.to_dict() for role in roles]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/roles', methods=['POST'])
def create_role():
    try:
        data = request.get_json()
        role = Role(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(role)
        db.session.commit()
        return jsonify({'message': 'Role created successfully', 'role': role.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
