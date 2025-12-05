from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Task, User, PerformanceReview
from datetime import datetime, timedelta
from genai.services import AIPerformanceReview
import json

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get tasks based on query parameters"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        assigned_to_id = request.args.get('assigned_to_id')
        assigned_by_id = request.args.get('assigned_by_id')
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        
        # Build query
        query = Task.query
        
        if assigned_to_id:
            query = query.filter_by(assigned_to_id=assigned_to_id)
        elif assigned_by_id:
            query = query.filter_by(assigned_by_id=assigned_by_id)
        else:
            # If no filters, return tasks related to current user
            query = query.filter(
                (Task.assigned_to_id == current_user_id) | 
                (Task.assigned_by_id == current_user_id)
            )
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by deadline
        query = query.order_by(Task.deadline.desc())
        
        if limit:
            query = query.limit(limit)
        
        tasks = query.all()
        
        # Add assigned user names
        task_list = []
        for task in tasks:
            task_dict = task.to_dict()
            assigned_to = User.query.get(task.assigned_to_id)
            if assigned_to:
                task_dict['assigned_to_name'] = assigned_to.name
            task_list.append(task_dict)
        
        return jsonify({
            'tasks': task_list,
            'total_count': len(task_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@task_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_tasks():
    """Get tasks for the current user for today"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get today's date range
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get tasks assigned to current user with deadline today or overdue
        tasks = Task.query.filter(
            Task.assigned_to_id == current_user_id,
            Task.deadline <= today_end,
            Task.status.in_(['pending', 'in_progress'])
        ).order_by(Task.deadline.asc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'total_count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@task_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get specific task details"""
    try:
        current_user_id = get_jwt_identity()
        task = Task.query.get_or_404(task_id)
        
        # Verify user has access to this task
        if task.assigned_to_id != current_user_id and task.assigned_by_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@task_bp.route('/<task_id>/employee-review', methods=['POST'])
@jwt_required()
def submit_employee_review(task_id):
    """Employee submits self-review for a task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.get_or_404(task_id)
        
        # Verify this is the assigned employee
        if task.assigned_to_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        task.employee_review = data.get('review')
        task.employee_reviewed_at = datetime.utcnow()
        task.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review submitted successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@task_bp.route('/<task_id>/manager-review', methods=['POST'])
@jwt_required()
def submit_manager_review(task_id):
    """Manager submits review for employee's task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.get_or_404(task_id)
        
        # Verify this is the assigning manager
        if task.assigned_by_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        task.manager_review = data.get('review')
        task.manager_reviewed_at = datetime.utcnow()
        task.status = 'reviewed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Manager review submitted successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@task_bp.route('/<task_id>/generate-ai-summary', methods=['POST'])
@jwt_required()
def generate_ai_summary(task_id):
    """Generate AI summary combining employee and manager reviews"""
    try:
        current_user_id = get_jwt_identity()
        task = Task.query.get_or_404(task_id)
        
        # Verify user has access
        if task.assigned_to_id != current_user_id and task.assigned_by_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if not task.employee_review or not task.manager_review:
            return jsonify({'error': 'Both employee and manager reviews are required'}), 400
        
        # Generate AI summary using existing service
        ai_review_service = AIPerformanceReview()
        ai_summary = ai_review_service.generate_performance_review(
            task.employee_review,
            task.manager_review
        )
        
        # Save AI summary to task
        task.ai_summary = json.dumps(ai_summary)
        task.ai_summary_generated_at = datetime.utcnow()
        
        # Also create a performance review record
        performance_review = PerformanceReview(
            employee_id=task.assigned_to_id,
            reviewer_id=task.assigned_by_id,
            type='task_performance_review',
            text=json.dumps({
                'task_id': task.id,
                'task_title': task.title,
                'employee_review': task.employee_review,
                'manager_review': task.manager_review,
                'ai_summary': ai_summary
            }),
            rating=None
        )
        
        db.session.add(performance_review)
        db.session.commit()
        
        return jsonify({
            'message': 'AI summary generated successfully',
            'task': task.to_dict(),
            'ai_summary': ai_summary,
            'performance_review_id': performance_review.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task (Manager only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Check if user is manager
        if current_user.role.name not in ['manager', 'hr']:
            return jsonify({'error': 'Only managers can create tasks'}), 403
        
        data = request.get_json()
        
        new_task = Task(
            title=data['title'],
            description=data.get('description'),
            assigned_to_id=data['assigned_to_id'],
            assigned_by_id=current_user_id,
            deadline=datetime.fromisoformat(data['deadline']),
            priority=data.get('priority', 'medium'),
            status='pending'
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': new_task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@task_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task status"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.get_or_404(task_id)
        
        # Verify user has access
        if task.assigned_to_id != current_user_id and task.assigned_by_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if 'status' in data:
            task.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500