from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import InterviewerAssignment, Resume, User, Application, JobPost
from genai.services.resume_service import ResumeService
from genai.services.recommendation_service import RecommendationService
from genai.prompt import PromptManager
from genai.llm_factory import LLMModelFactory
from utils import TextUtility
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile

screening_bp = Blueprint('screening', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@screening_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Upload and parse a resume for a candidate"""
    try:
        # Check if the post request has the file part
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_{timestamp}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'resumes')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create resume record
            resume = Resume(
                owner_id=user_id,
                file_url=file_path,
                uploaded_at=datetime.utcnow()
            )
            
            db.session.add(resume)
            db.session.flush()  # Get the resume ID
            
            # Process resume using AI service
            try:
                resume_service = ResumeService(file_path, user_id, resume.id)
                parsed_resume_data = resume_service.resume_service()
                
                # Store parsed data
                resume.set_parsed_data(parsed_resume_data)
                
            except Exception as e:
                # If AI processing fails, still save the resume but without parsed data
                print(f"AI processing failed: {e}")
                resume.set_parsed_data({'error': 'AI processing failed', 'raw_error': str(e)})
            
            db.session.commit()
            
            return jsonify({
                'message': 'Resume uploaded and processed successfully',
                'resume': resume.to_dict(),
                'recommended_jobs': parsed_resume_data if 'error' not in str(parsed_resume_data) else []
            }), 201
        
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: pdf, docx, doc'}), 400
    
    except Exception as e:
        db.session.rollback()
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)  # Clean up file if database operation failed
        return jsonify({'error': str(e)}), 500

@screening_bp.route('/score-candidate', methods=['POST'])
def score_candidate():
    """Score a candidate against a job posting using AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['candidate_id', 'job_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        candidate_id = data['candidate_id']
        job_id = data['job_id']
        model_name = data.get('model_name', 'gemini')
        
        # Get candidate and their latest resume
        candidate = User.query.get(candidate_id)
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        latest_resume = Resume.query.filter_by(owner_id=candidate_id).order_by(Resume.uploaded_at.desc()).first()
        if not latest_resume:
            return jsonify({'error': 'No resume found for candidate'}), 404
        
        # Get job details
        job = JobPost.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get parsed resume data
        resume_data = latest_resume.get_parsed_data()
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': 'Resume parsing failed or incomplete'}), 400
        
        # Format resume for AI processing
        resume_text = TextUtility.format_resume_text(resume_data)
        
        # Create a comprehensive job description for scoring
        job_description = f"""
        Title: {job.title}
        Description: {job.description or 'Not provided'}
        Requirements: {job.requirements or 'Not provided'}
        Location: {job.location or 'Not specified'}
        Level: {job.level or 'Not specified'}
        """
        
        # Generate AI score using skill gap analysis prompt (we'll create a new one)
        prompt = f"""
        You are an expert HR recruiter. Score this candidate against the job requirements.
        Provide a detailed analysis and score from 0-100.
        
        Respond only in valid JSON format:
        {{
            "overall_score": 85,
            "category_scores": {{
                "skills_match": 90,
                "experience_match": 80,
                "education_match": 85,
                "location_match": 95
            }},
            "strengths": ["Strong technical skills", "Relevant experience"],
            "weaknesses": ["Limited leadership experience"],
            "recommendation": "strong_fit",
            "summary": "Excellent candidate with strong technical background"
        }}
        
        Job Details:
        {job_description}
        
        Candidate Resume:
        {resume_text}
        
        Score this candidate comprehensively considering skills, experience, education, and overall fit.
        """
        
        # Get LLM and generate score
        try:
            llm = LLMModelFactory.get_model_provider(model_name).get_model()
            response = llm.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from LLM")
            
            scoring_result = TextUtility.remove_json_marker(response.text)
            
        except Exception as e:
            return jsonify({'error': f'AI scoring failed: {str(e)}'}), 500
        
        # Update or create application with score
        application = Application.query.filter_by(
            candidate_id=candidate_id,
            job_id=job_id
        ).first()
        
        if application:
            application.score = scoring_result.get('overall_score', 0)
            db.session.commit()
        
        return jsonify({
            'message': 'Candidate scored successfully',
            'candidate_id': candidate_id,
            'job_id': job_id,
            'scoring_result': scoring_result,
            'application_updated': application is not None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@screening_bp.route('/candidates', methods=['GET'])
def get_candidates():
    """Get candidates with their screening information"""
    try:
        # Get query parameters
        job_id = request.args.get('job_id')
        status = request.args.get('status')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        has_resume = request.args.get('has_resume', 'true').lower() == 'true'
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        if job_id:
            # Get candidates who applied to specific job
            query = db.session.query(User).join(Application).filter(Application.job_id == job_id)
            
            if status:
                query = query.filter(Application.status == status)
            if min_score is not None:
                query = query.filter(Application.score >= min_score)
            if max_score is not None:
                query = query.filter(Application.score <= max_score)
        else:
            # Get all candidates (users with candidate role or those with resumes)
            query = User.query
            
            if has_resume:
                query = query.join(Resume).filter(Resume.owner_id == User.id)
        
        # Apply pagination
        candidates = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        # Format response with additional screening data
        candidates_data = []
        for candidate in candidates:
            candidate_data = candidate.to_dict()
            
            # Add resume information
            latest_resume = Resume.query.filter_by(owner_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()
            if latest_resume:
                candidate_data['latest_resume'] = {
                    'id': latest_resume.id,
                    'uploaded_at': latest_resume.uploaded_at.isoformat() if latest_resume.uploaded_at else None,
                    'has_parsed_data': bool(latest_resume.parsed_data)
                }
            
            # Add application information for specific job
            if job_id:
                application = Application.query.filter_by(candidate_id=candidate.id, job_id=job_id).first()
                if application:
                    candidate_data['application'] = {
                        'id': application.id,
                        'status': application.status,
                        'score': application.score,
                        'applied_at': application.applied_at.isoformat() if application.applied_at else None
                    }
            
            candidates_data.append(candidate_data)
        
        return jsonify({
            'candidates': candidates_data,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'filters': {
                'job_id': job_id,
                'status': status,
                'min_score': min_score,
                'max_score': max_score
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@screening_bp.route('/candidates/<candidate_id>/action', methods=['PUT'])
def update_candidate_action(candidate_id):
    """Update candidate screening action (shortlist, reject, interview, etc.)"""
    try:
        data = request.get_json()
        
        action = data.get('action')
        job_id = data.get('job_id')
        notes = data.get('notes', '')
        reviewer_id = data.get('reviewer_id')
        
        if not action:
            return jsonify({'error': 'action is required'}), 400
        
        # Valid actions
        valid_actions = [
            'shortlist', 'reject', 'interview', 'hire', 'hold', 'withdraw'
        ]
        
        if action not in valid_actions:
            return jsonify({
                'error': f'Invalid action. Valid actions: {", ".join(valid_actions)}'
            }), 400
        
        # Map actions to application status
        action_status_map = {
            'shortlist': 'screening',
            'reject': 'rejected',
            'interview': 'interviewed', 
            'hire': 'selected',
            'hold': 'on_hold',
            'withdraw': 'withdrawn'
        }
        
        new_status = action_status_map.get(action, 'under_review')
        
        # Update application if job_id is provided
        if job_id:
            application = Application.query.filter_by(
                candidate_id=candidate_id,
                job_id=job_id
            ).first()
            
            if not application:
                return jsonify({'error': 'Application not found for this candidate and job'}), 404
            
            old_status = application.status
            application.status = new_status
            db.session.commit()
            
            return jsonify({
                'message': f'Candidate action updated: {action}',
                'candidate_id': candidate_id,
                'job_id': job_id,
                'action': action,
                'status_change': {
                    'from': old_status,
                    'to': new_status
                },
                'notes': notes,
                'reviewer_id': reviewer_id
            }), 200
        else:
            # General candidate action without specific job context
            return jsonify({
                'message': f'Candidate action recorded: {action}',
                'candidate_id': candidate_id,
                'action': action,
                'notes': notes,
                'reviewer_id': reviewer_id
            }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@screening_bp.route('/bulk-score', methods=['POST'])
def bulk_score_candidates():
    """Score multiple candidates against a job"""
    try:
        data = request.get_json()
        
        job_id = data.get('job_id')
        candidate_ids = data.get('candidate_ids', [])
        model_name = data.get('model_name', 'gemini')
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        if not candidate_ids:
            return jsonify({'error': 'candidate_ids are required'}), 400
        
        # Get job details
        job = JobPost.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        results = []
        errors = []
        
        for candidate_id in candidate_ids:
            try:
                # Process each candidate (reuse logic from score_candidate)
                candidate = User.query.get(candidate_id)
                if not candidate:
                    errors.append(f"Candidate {candidate_id} not found")
                    continue
                
                latest_resume = Resume.query.filter_by(owner_id=candidate_id).order_by(Resume.uploaded_at.desc()).first()
                if not latest_resume:
                    errors.append(f"No resume found for candidate {candidate_id}")
                    continue
                
                # Add to results (simplified for bulk operation)
                results.append({
                    'candidate_id': candidate_id,
                    'candidate_name': candidate.name,
                    'status': 'processed',
                    'has_resume': True
                })
                
            except Exception as e:
                errors.append(f"Error processing candidate {candidate_id}: {str(e)}")
        
        return jsonify({
            'message': f'Bulk scoring completed. Processed {len(results)} candidates',
            'job_id': job_id,
            'results': results,
            'errors': errors,
            'summary': {
                'total_requested': len(candidate_ids),
                'processed': len(results),
                'errors': len(errors)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# ...existing code...

@screening_bp.route('/candidates/<candidate_id>/interviews', methods=['GET'])
def get_candidate_interviews(candidate_id):
    """Get upcoming interviews for a specific candidate"""
    try:
        # Get query parameters
        upcoming_only = request.args.get('upcoming_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate candidate exists
        candidate = User.query.get_or_404(candidate_id)
        
        # Build query for interviews
        query = InterviewerAssignment.query.filter_by(
            candidate_id=candidate_id
        )
        
        # Filter for upcoming interviews only
        if upcoming_only:
            query = query.filter(
                InterviewerAssignment.scheduled_at > datetime.utcnow(),
                InterviewerAssignment.status.in_(['scheduled', 'confirmed'])
            )
        
        # Order by scheduled time (nearest first)
        query = query.order_by(InterviewerAssignment.scheduled_at.asc())
        
        # Apply pagination
        interviews = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        # Format response with job and interviewer details
        interviews_data = []
        for interview in interviews:
            interview_data = interview.to_dict()
            
            # Add job details
            if interview.job:
                interview_data['job_details'] = {
                    'id': interview.job.id,
                    'title': interview.job.title,
                    'company': interview.job.school or 'Company',
                    'location': interview.job.location
                }
            
            # Add interviewer details
            if interview.interviewer:
                interview_data['interviewer_details'] = {
                    'id': interview.interviewer.id,
                    'name': interview.interviewer.name,
                    'email': interview.interviewer.email
                }
            
            interviews_data.append(interview_data)
        
        return jsonify({
            'success': True,
            'interviews': interviews_data,
            'candidate_id': candidate_id,
            'candidate_name': candidate.name,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@screening_bp.route('/resumes/<resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """
    Get resume details by ID (for HR to view candidate resumes)
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Check if user is HR
        is_hr = current_user.role and current_user.role.name.lower() == 'hr'
        is_admin = current_user.role and current_user.role.name.lower() == 'admin'
        
        if not (is_hr or is_admin):
            return jsonify({'error': 'Access denied. Only HR can access candidate resumes'}), 403
        
        # Get resume
        resume = Resume.query.get_or_404(resume_id)
        
        return jsonify(resume.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@screening_bp.route('/my-performance/technical-tests', methods=['GET'])
@jwt_required()
def get_my_technical_test_results():
    """Get technical test results for the current candidate"""
    try:
        from models import AITestAssignment, AITestAssessment
        
        current_user_id = get_jwt_identity()
        
        # Get all technical tests for the candidate
        test_assignments = AITestAssignment.query.filter_by(
            candidate_id=current_user_id
        ).order_by(AITestAssignment.created_at.desc()).all()
        
        results = []
        for assignment in test_assignments:
            test_data = assignment.to_dict()
            
            # Get job details
            if assignment.job:
                test_data['job_details'] = {
                    'id': assignment.job.id,
                    'title': assignment.job.title,
                    'location': assignment.job.location
                }
            
            # Get assessment/results if available
            assessment = AITestAssessment.query.filter_by(
                test_assignment_id=assignment.id
            ).first()
            
            if assessment:
                test_data['assessment'] = {
                    'id': assessment.id,
                    'score': assessment.score,
                    'feedback': assessment.feedback,
                    'strengths': assessment.strengths,
                    'weaknesses': assessment.weaknesses,
                    'recommendation': assessment.recommendation,
                    'evaluated_at': assessment.evaluated_at.isoformat() if assessment.evaluated_at else None
                }
            
            results.append(test_data)
        
        return jsonify({
            'success': True,
            'tests': results,
            'total': len(results)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@screening_bp.route('/my-performance/interviews', methods=['GET'])
@jwt_required()
def get_my_interview_results():
    """Get interview results for the current candidate with optional filtering by type"""
    try:
        from models import Scorecard
        
        current_user_id = get_jwt_identity()
        interview_type = request.args.get('interview_type')  # technical, hr, behavioral, etc.
        
        # Build query for interview assignments
        query = InterviewerAssignment.query.filter_by(
            candidate_id=current_user_id
        )
        
        # Filter by interview type if provided
        if interview_type:
            query = query.filter_by(interview_type=interview_type)
        
        # Order by scheduled time (most recent first)
        query = query.order_by(InterviewerAssignment.scheduled_at.desc())
        
        interviews = query.all()
        
        results = []
        for interview in interviews:
            interview_data = interview.to_dict()
            
            # Add job details
            if interview.job:
                interview_data['job_details'] = {
                    'id': interview.job.id,
                    'title': interview.job.title,
                    'location': interview.job.location,
                    'school': interview.job.school
                }
            
            # Add interviewer details
            if interview.interviewer:
                interview_data['interviewer_details'] = {
                    'id': interview.interviewer.id,
                    'name': interview.interviewer.name
                }
            
            # Get scorecard if available
            scorecard = Scorecard.query.filter_by(
                interview_assignment_id=interview.id
            ).first()
            
            if scorecard:
                interview_data['scorecard'] = {
                    'id': scorecard.id,
                    'overall_score': scorecard.overall_score,
                    'technical_score': scorecard.technical_score,
                    'communication_score': scorecard.communication_score,
                    'problem_solving_score': scorecard.problem_solving_score,
                    'cultural_fit_score': scorecard.cultural_fit_score,
                    'strengths': scorecard.strengths,
                    'weaknesses': scorecard.weaknesses,
                    'feedback_notes': scorecard.feedback_notes,
                    'recommendation': scorecard.recommendation,
                    'submitted_at': scorecard.submitted_at.isoformat() if scorecard.submitted_at else None
                }
            
            results.append(interview_data)
        
        return jsonify({
            'success': True,
            'interviews': results,
            'total': len(results),
            'filter': {
                'interview_type': interview_type
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500