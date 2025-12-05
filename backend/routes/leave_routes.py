from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, LeaveBalance, LeaveRecord
from datetime import datetime

leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/adjust', methods=['POST'])
def adjust_leave():
    try:
        data = request.get_json()

        # Get the employee and leave balance
        employee = User.query.get_or_404(data['employee_id'])
        balance = LeaveBalance.query.filter_by(employee_id=employee.id).first()

        # If no leave balance exists, create one
        if not balance:
            balance = LeaveBalance(employee_id=employee.id)
            db.session.add(balance)
        
        leave_type = data['leave_type']
        days = data['days']
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        reason = data.get('reason', '')

        # Adjust leave based on type
        deduction = 0
        if leave_type == 'Sick':
            balance.sick_leave = max(0, balance.sick_leave - days)
        elif leave_type == 'Casual':
            balance.casual_leave = max(0, balance.casual_leave - days)
        elif leave_type == 'LOP':
            balance.lop_leave += days
            deduction = days * 100  # example: 100 currency units per day of unpaid leave

        # Create a leave record
        record = LeaveRecord(
            employee_id=employee.id,
            leave_type=leave_type,
            days=days,
            date=date,
            reason=reason
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'employee': employee.name,
                'remaining_leave': balance.sick_leave + balance.casual_leave,
                'deduction': deduction,
                'leave_balance': {
                    'sick': balance.sick_leave,
                    'casual': balance.casual_leave,
                    'lop': balance.lop_leave
                }
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/history', methods=['GET'])
def get_leave_history():
    try:
        employee_id = request.args.get('employee_id', None)

        if employee_id:
            records = LeaveRecord.query.filter_by(employee_id=employee_id).order_by(LeaveRecord.created_at.desc()).all()
        else:
            records = LeaveRecord.query.order_by(LeaveRecord.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/balance/<employee_id>', methods=['GET'])
def get_leave_balance(employee_id):
    try:
        employee = User.query.get_or_404(employee_id)

        balance = LeaveBalance.query.filter_by(employee_id=employee.id).first()
        if not balance:
            # Initialize default balance if not present
            balance = LeaveBalance(employee_id=employee.id)
            db.session.add(balance)
            db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'employee': employee.name,
                'leave_balance': {
                    'sick': balance.sick_leave,
                    'casual': balance.casual_leave,
                    'lop': balance.lop_leave
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/types', methods=['GET'])
def get_leave_types():
    try:
        leave_types = ['Sick', 'Casual', 'LOP']
        
        return jsonify({
            'success': True,
            'data': leave_types
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/request', methods=['POST'])
def request_leave():
    try:
        data = request.get_json()

        employee_id = data['employee_id']
        leave_type = data['leave_type']
        days = data['days']
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        reason = data.get('reason', '')

        # Validate employee and leave type
        employee = User.query.get_or_404(employee_id)
        if leave_type not in ['Sick', 'Casual', 'LOP']:
            return jsonify({'error': 'Invalid leave type'}), 400

        # Create the pending leave record
        leave_record = LeaveRecord(
            employee_id=employee.id,
            leave_type=leave_type,
            days=days,
            date=start_date,
            reason=reason,
            status='Pending'
        )

        db.session.add(leave_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Leave request submitted successfully',
            'data': {
                'leave_id': leave_record.id,
                'status': leave_record.status
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/approve/<leave_id>', methods=['PUT'])
def approve_leave(leave_id):
    try:
        # Get the leave record
        leave = LeaveRecord.query.get_or_404(leave_id)

        if leave.status != 'Pending':
            return jsonify({'error': 'Leave already processed'}), 400

        # Get employee and balance
        employee = User.query.get_or_404(leave.employee_id)
        balance = LeaveBalance.query.filter_by(employee_id=employee.id).first()
        if not balance:
            balance = LeaveBalance(employee_id=employee.id)
            db.session.add(balance)

        # Deduct from the correct leave type balance
        if leave.leave_type == 'Sick':
            balance.sick_leave = max(0, balance.sick_leave - leave.days)
        elif leave.leave_type == 'Casual':
            balance.casual_leave = max(0, balance.casual_leave - leave.days)
        elif leave.leave_type == 'LOP':
            balance.lop_leave += leave.days  # LOP increases for unpaid days

        # Update status
        leave.status = 'Approved'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Leave approved successfully',
            'data': {
                'leave_id': leave.id,
                'employee': employee.name,
                'new_balance': {
                    'sick': balance.sick_leave,
                    'casual': balance.casual_leave,
                    'lop': balance.lop_leave
                }
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leave_bp.route('/reject/<leave_id>', methods=['PUT'])
def reject_leave(leave_id):
    try:
        # Get the leave record
        leave = LeaveRecord.query.get_or_404(leave_id)

        if leave.status != 'Pending':
            return jsonify({'error': 'Leave already processed'}), 400

        # Update status
        leave.status = 'Rejected'
        db.session.commit()

        employee = User.query.get(leave.employee_id)

        return jsonify({
            'success': True,
            'message': 'Leave rejected successfully',
            'data': {
                'leave_id': leave.id,
                'employee': employee.name if employee else None,
                'status': leave.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@leave_bp.route('/<leave_id>', methods=['DELETE'])
@jwt_required()
def delete_leave(leave_id):
    try:
        current_user_id = get_jwt_identity()
        leave = LeaveRecord.query.get_or_404(leave_id)

        # Only the owner can delete their leave record (and only if not approved)
        if leave.employee_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        if leave.status == 'Approved':
            return jsonify({'error': 'Cannot delete an approved leave'}), 400

        db.session.delete(leave)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Leave deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
