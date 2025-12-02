from flask import Blueprint, request, jsonify
from app import db
from models import Training, Course, Enrollment, User
from datetime import datetime

training_bp = Blueprint('training', __name__)

# GET /api/training/modules
@training_bp.route('/modules', methods=['GET'])
def list_modules():
    try:
        # optional query param to filter by training_id
        training_id = request.args.get('training_id')
        if training_id:
            courses = Course.query.filter_by(training_id=training_id).all()
        else:
            courses = Course.query.all()

        data = []
        for c in courses:
            data.append({
                'id': c.id,
                'title': c.title,
                'training_id': c.training_id,
                'training_title': c.training.title if c.training else None,
                'content_url': c.content_url,
                'duration_mins': c.duration_mins
            })

        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# GET /api/training/modules/<id>
@training_bp.route('/modules/<module_id>', methods=['GET'])
def get_module(module_id):
    try:
        c = Course.query.get_or_404(module_id)
        payload = {
            'id': c.id,
            'title': c.title,
            'training_id': c.training_id,
            'training_title': c.training.title if c.training else None,
            'content_url': c.content_url,
            'duration_mins': c.duration_mins
        }

        # optional-- if user_id provided, include user's enrollment info for this module
        user_id = request.args.get('user_id')
        if user_id:
            enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=c.id).first()
            payload['enrollment'] = enrollment.to_dict() if enrollment else None

        return jsonify({'success': True, 'data': payload}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PUT /api/training/modules/<id>/progress
@training_bp.route('/modules/<module_id>/progress', methods=['PUT'])
def update_module_progress(module_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        progress = float(data.get('progress', 0))

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        if progress < 0 or progress > 100:
            return jsonify({'error': 'progress must be between 0 and 100'}), 400

        # ensure module exists
        course = Course.query.get_or_404(module_id)

        # find or create enrollment
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course.id).first()
        if not enrollment:
            enrollment = Enrollment(user_id=user_id, course_id=course.id, progress=0.0, status='enrolled')
            db.session.add(enrollment)

        enrollment.progress = progress
        # if progress == 100, you may optionally set status
        if progress >= 100:
            enrollment.status = 'completed'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Progress updated',
            'data': {
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'progress': enrollment.progress,
                'status': enrollment.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# POST /api/training/modules/<id>/complete
@training_bp.route('/modules/<module_id>/complete', methods=['POST'])
def complete_module(module_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        course = Course.query.get_or_404(module_id)

        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course.id).first()
        if not enrollment:
            # create enrollment if missing and mark completed
            enrollment = Enrollment(
                user_id=user_id,
                course_id=course.id,
                progress=100.0,
                status='completed'
            )
            db.session.add(enrollment)
        else:
            enrollment.progress = 100.0
            enrollment.status = 'completed'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Module marked as complete',
            'data': {
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'progress': enrollment.progress,
                'status': enrollment.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
