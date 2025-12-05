from flask import Blueprint, request, jsonify
from app import db
from models import Application, User, JobPost, Resume, Vacancy, Role
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required

application_bp = Blueprint('applications', __name__)

@application_bp.route('/submit', methods=['POST'])
def submit_application():
    """Submit a new job application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['candidate_id', 'resume_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Determine if applying to job or vacancy
        job_id = data.get('job_id')
        vacancy_id = data.get('vacancy_id')
        cover_letter = data.get('cover_letter')
        expected_salary = data.get('expected_salary')
        availability = data.get('availability')
        source = data.get('source')
        
        if not job_id:
            return jsonify({'error': 'Either job_id or vacancy_id is required'}), 400
        
        if job_id and vacancy_id:
            return jsonify({'error': 'Cannot apply to both job and vacancy simultaneously'}), 400
        
        # Validate that the entities exist
        candidate = User.query.get(data['candidate_id'])
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        resume = Resume.query.get(data['resume_id'])
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        if vacancy_id:
            vacancy = Vacancy.query.get(vacancy_id)
            if not vacancy:
                return jsonify({'error': 'Vacancy not found'}), 404
        
        if not cover_letter:
            return jsonify({'error': 'Cover letter is required'}), 400
        
        if not availability:
            return jsonify({'error': 'Availability is required'}), 400
        
        if not source:
            return jsonify({'error': 'Source is required'}), 400
        
        if len(cover_letter) < 10 or len(cover_letter) > 1000:
            return jsonify({'error': 'Cover letter must be between 10 and 1000 characters'}), 400
        

        if job_id:
            job = JobPost.query.get(job_id)
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
        
            # Check if already applied
            existing_application = Application.query.filter_by(
                candidate_id=data['candidate_id'],
                job_id=job_id
            ).first()
            
            if existing_application:
                return jsonify({'error': 'Already applied to this job'}), 400
        
        # Create new application
        application = Application(
            candidate_id=data['candidate_id'],
            job_id=job_id,
            resume_id=data['resume_id'],
            status=data.get('status', 'applied'),
            score=data.get('score'),
            cover_letter=cover_letter,
            expected_salary=expected_salary,
            availability=availability,
            source=source
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    """Get applications with optional filtering"""
    try:
        # Get query parameters for filtering
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        role=Role.query.filter_by(id=user.role_id).first()
        job_id = request.args.get('job_id')
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query with filters
        query = Application.query
        
        if user.role_id == role.id and role.name == 'candidate':
            query = query.filter(Application.candidate_id == current_user_id)
        if user.role_id == role.id and role.name in ['hr', 'admin']:
            query = query.filter(Application.job_id == job_id)
        if job_id:
            query = query.filter(Application.job_id == job_id)
        if status:
            query = query.filter(Application.status == status)
        
        # Order by most recent first
        query = query.order_by(Application.applied_at.desc())
        
        # Apply pagination
        applications = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return jsonify({
            'applications': [app.to_dict() for app in applications],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_bp.route('/<application_id>', methods=['GET'])
def get_application(application_id):
    """Get a specific application by ID"""
    try:
        application = Application.query.get_or_404(application_id)
        
        # Get additional details
        application_data = application.to_dict()
        
        # Add resume data if available
        if application.resume:
            application_data['resume_details'] = application.resume.to_dict()
        
        # Add job details if available
        if application.job:
            application_data['job_details'] = application.job.to_dict()
        
        # Add candidate details
        if application.candidate:
            application_data['candidate_details'] = {
                'id': application.candidate.id,
                'name': application.candidate.name,
                'email': application.candidate.email
            }
        
        return jsonify(application_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application_bp.route('/<application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    """Update application status"""
    try:
        application_id = request.view_args['application_id']
        application = Application.query.get_or_404(application_id)
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        # Valid status values
        valid_statuses = [
            'applied', 'under_review', 'screening', 'interviewed',
            'selected', 'rejected', 'withdrawn', 'on_hold'
        ]
        
        new_status = data['status']
        if new_status not in valid_statuses:
            return jsonify({
                'error': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'
            }), 400
        
        # Update application status
        old_status = application.status
        application.status = new_status
        
        # Update score if provided
        if 'score' in data:
            application.score = data['score']
        
        # Add notes if provided (we'll need to add notes field later)
        notes = data.get('notes', '')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Application status updated successfully',
            'application': application.to_dict(),
            'status_change': {
                'from': old_status,
                'to': new_status,
                'notes': notes
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/bulk-status', methods=['PUT'])
def bulk_update_status():
    """Update status for multiple applications"""
    try:
        data = request.get_json()
        
        application_ids = data.get('application_ids', [])
        new_status = data.get('status')
        
        if not application_ids:
            return jsonify({'error': 'application_ids are required'}), 400
        
        if not new_status:
            return jsonify({'error': 'status is required'}), 400
        
        # Update all applications
        updated_count = Application.query.filter(
            Application.id.in_(application_ids)
        ).update({Application.status: new_status}, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated status for {updated_count} applications',
            'updated_count': updated_count,
            'new_status': new_status
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@application_bp.route('/stats', methods=['GET'])
def get_application_stats():
    """Get application statistics"""
    try:
        job_id = request.args.get('job_id')
        
        # Base query
        query = Application.query
        if job_id:
            query = query.filter(Application.job_id == job_id)
        
        # Get status counts
        status_counts = {}
        statuses = ['applied', 'under_review', 'shortlisted', 'interviewed', 'selected', 'rejected']
        
        for status in statuses:
            count = query.filter(Application.status == status).count()
            status_counts[status] = count
        
        # Get total applications
        total_applications = query.count()
        
        # Get recent applications (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_applications = query.filter(Application.applied_at >= week_ago).count()
        
        return jsonify({
            'total_applications': total_applications,
            'recent_applications': recent_applications,
            'status_breakdown': status_counts,
            'job_id': job_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500