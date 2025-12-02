from flask import Blueprint, request, jsonify
from app import db
from models import (
    User, Role, Notification, Interview, Application
)
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime

notification_bp = Blueprint('notifications', __name__)

# create notifications

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user_id = get_jwt_identity()
    
    try:
        current_user = User.query.get_or_404(current_user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        notifications = Notification.query.order_by(Notification.created_at.desc()).all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# mark notification as read
@notification_bp.route('mark-read/<string:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        notification.read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# send notification
@notification_bp.route('/sends', methods=['POST'])
def send_notification():
    try:
        data=request.get_json() or {}
        receiptient_id = data.get('recipient_id')
        message = data.get('message')
        if not data or 'recipient_id' not in data or 'message' not in data:
            return jsonify({'error': 'Missing recipient_id or message'}), 400
        notification = Notification(recipient_id=receiptient_id, message=message, read=False)
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': 'Notification sent successfully', 'notification': notification.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

# get notification settings
@notification_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    current_user_id = get_jwt_identity()
    
    try:
        current_user = User.query.get_or_404(current_user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        settings = {
            'email_notificatins': current_user.email_notification,
            'sms_notifications': current_user.sms_notification
        }
        return jsonify(settings), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



#candidate receive interview exam notification
@notification_bp.route('/exam', methods=['POST'])
@jwt_required()
def send_exam_notification():
    current_user_id = get_jwt_identity()
    try:
        current_user = User.query.get_or_404(current_user_id)
        role = Role.query.filter_by(id=current_user.role_id).first()
        if (current_user.role_id == role.id) & (role.name == "candidate"):
            data = request.get_json() or {}
            message = data.get('message', 'you have an interview exam')
            notification = Notification(recipient_id=current_user_id, message=message, read=False)
            db.session.add(notification)
            db.session.commit()
            return jsonify({'message': 'Notification sent successfully', 'notification': notification.to_dict()}), 201
        else:
            return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# exam complete notification
@notification_bp.route('/exam-complete', methods=['POST'])
@jwt_required()
def notify_hr_on_exam_complete():
    current_user_id = get_jwt_identity()
    try:
        current_user = User.query.get_or_404(current_user_id)
        role=Role.query.filter_by(id=current_user.role_id).first()
        if (current_user.role_id == role.id) & (role.name == "candidate"):
            data = request.get_json() or {}
            message = data.get('message', 'your interview exam is complete')
            
            hr_roles = Role.query.filter_by(name='hr').first()
            hr_users = User.query.filter_by(role_id=hr_roles.id).all()
            for hr_user in hr_users:
                notification = Notification(recipient_id=hr_user.id, message=f"Candidate {current_user.name} has completed their interview.", read=False)
                db.session.add(notification)
                db.session.commit()
            return jsonify({'message': 'Notifications sent successfully'}), 201
        else:
            return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


#notify to managers who are free
@notification_bp.route('/free-manager', methods=['GET'])
@jwt_required()
def get_free_managers():
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    role=Role.query.filter_by(id=current_user.role_id).first()
    if (current_user.role_id == role.id) & (role.name == "hr"):
        manager_role=Role.query.filter_by(name='manager').first()
        all_managers = User.query.filter_by(role_id=manager_role.id).all()
        if not all_managers:
            return jsonify({'error': 'No managers found'}), 404
        free_managers = User.query.filter_by(role_id=manager_role.id, status='active').all()
        return jsonify([manager.to_dict() for manager in free_managers]), 200
    else:
        return jsonify({'error': 'Unauthorized'}), 401
    


# notify managers who are free by HR to interview candidates
@notification_bp.route('/notify-manager/<manager_id>', methods=['POST'])
@jwt_required()
def notify_manager(manager_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    role=Role.query.filter_by(id=current_user.role_id).first()
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    data=request.get_json() or {}

    candidate_id = data.get('candidate_id')
    custom_message = data.get('message')

    candidate = User.query.get_or_404(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    manager = User.query.get_or_404(manager_id)
    if not manager:
        return jsonify({'error': 'Manager not found'}), 404
    
    message = custom_message or f"you are requested to interview {candidate.name}"

    try:
        notification = Notification(recipient_id=manager.id, message=message, read=False)
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': 'Notification sent successfully', 'notification': notification.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500