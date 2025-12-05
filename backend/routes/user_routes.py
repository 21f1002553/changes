from flask import Blueprint, request, jsonify
from app import db
from models import User, Role, Notification, PerformanceReview
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('users', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        role = Role.query.filter_by(id=current_user.role_id).first()
        if (current_user.role_id == role.id) and (role.name == "candidate"):
            users = User.query.filter_by(id=current_user_id).first()
            return jsonify(users.to_dict()), 200
        elif (current_user.role_id == role.id) and (role.name == "hr"):
            users = User.query.filter_by(id=current_user_id).first()
            return jsonify(users.to_dict()), 200
        elif (current_user.role_id == role.id) and (role.name == "bda"):
            users = User.query.filter_by(id=current_user_id).first()
            return jsonify(users.to_dict()), 200
        elif (current_user.role_id == role.id) and (role.name == "ho"):
            users = User.query.filter_by(id=current_user_id).first()
            return jsonify(users.to_dict()), 200
            
        else:
            return jsonify({'error': 'Unauthorized role'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    role = Role.query.filter_by(id=current_user.role_id).first()
    if (current_user.role_id == role.id) and (role.name != "admin"):
        return jsonify({'error': 'Only admins can add users'}), 403
    try:
        data = request.get_json()
        existing_user = User.query.filter_by(email=data.get('email')).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        if 'name' not in data or 'email' not in data or 'role_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        # Generate default password if not provided
        password = data.get('password', 'TempPass123!')
        user = User(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(password),
            role_id=data['role_id'],
            status=data.get('status', 'active')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    role = Role.query.filter_by(id=current_user.role_id).first()
    # Compare role_id as string since DB stores as VARCHAR
    if (current_user.role_id == role.id) & (role.name != "admin"):
        return jsonify({'error': 'Only admins can update users'}), 403
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Email update: check for duplicates, only if changing
        new_email = data.get('email')
        if new_email and new_email != user.email:
            if User.query.filter(User.email == new_email, User.id != user.id).first():
                return jsonify({'error': 'Email already exists'}), 400
            user.email = new_email

        # Name update
        if 'name' in data:
            user.name = data['name']

        # Role update
        if 'role_id' in data:
            user.role_id = data['role_id']

        # Status update
        if 'status' in data:
            user.status = data['status']

        db.session.commit()
        return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    role = Role.query.filter_by(id=current_user.role_id).first()
    if (current_user.role_id == role.id) & (role.name != "admin"):
        return jsonify({'error': 'Only admins can delete users'}), 403
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/change-password', methods=['POST'])
@jwt_required()
def change_password(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if 'old_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Missing password fields'}), 400
        old_password = data['old_password']
        new_password = data['new_password']
        if not check_password_hash(user.password, old_password):
            return jsonify({'error': 'Old password is incorrect'}), 400
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/role/<string:role_name>', methods=['GET'])
@jwt_required()
def get_users_by_role_name(role_name):
    try:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        users = User.query.filter_by(role_id=role.id).all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_all_roles():
    try:
        roles = Role.query.all()
        return jsonify([role.to_dict() for role in roles]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications(user_id):
    try:
        notifications = Notification.query.filter_by(recipient_id=user_id).order_by(Notification.created_at.desc()).all()
        return jsonify([notification.to_dict() for notification in notifications]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/notifications', methods=['POST'])
@jwt_required()
def create_notification(user_id):
    try:
        data = request.get_json()
        if 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        notification = Notification(
            recipient_id=user_id,
            message=data['message'],
            read=data.get('read', False)
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': 'Notification created successfully', 'notification': notification.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/notifications/<string:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(user_id, notification_id):
    try:
        notification = Notification.query.filter_by(id=notification_id, recipient_id=user_id).first_or_404()
        notification.read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/performance-reviews', methods=['GET'])
@jwt_required()
def get_user_performance_reviews(user_id):
    try:
        reviews = PerformanceReview.query.filter_by(employee_id=user_id).order_by(PerformanceReview.created_at.desc()).all()
        return jsonify([review.to_dict() for review in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<string:user_id>/performance-reviews', methods=['POST'])
@jwt_required()
def create_performance_review(user_id):
    try:
        data = request.get_json()
        if 'reviewer_id' not in data or 'type' not in data:
            return jsonify({'error': 'Missing required review fields'}), 400
        review = PerformanceReview(
            employee_id=user_id,
            reviewer_id=data.get('reviewer_id'),
            type=data.get('type'),
            text=data.get('text', ''),
            rating=data.get('rating')
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({'message': 'Performance review created successfully', 'review': review.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
