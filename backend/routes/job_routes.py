from flask import Blueprint, request, jsonify
from app import db
from models import JobPost
from genai.services.recommendation_service import RecommendationService
from genai.prompt import PromptManager
from genai.llm_factory import LLMModelFactory
from utils import TextUtility

job_bp = Blueprint('jobs', __name__)

@job_bp.route('/', methods=['GET'])
def get_jobs():
    try:
        jobs = JobPost.query.all()
        return jsonify([job.to_dict() for job in jobs]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job = JobPost.query.get_or_404(job_id)
        return jsonify(job.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/', methods=['POST'])
def create_job():
    try:
        data = request.get_json()
        
        job = JobPost(
            title=data['title'],
            description=data.get('description', ''),
            requirements=data.get('requirements', ''),
            location=data.get('location', ''),
            school=data.get('school', ''),
            level=data.get('level', ''),
            posted_by_id=data['posted_by_id'],
            status=data.get('status', 'active')
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'message': 'Job post created successfully', 'job': job.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/<job_id>', methods=['PUT'])
def update_job(job_id):
    try:
        job = JobPost.query.get_or_404(job_id)
        data = request.get_json()
        
        job.title = data.get('title', job.title)
        job.description = data.get('description', job.description)
        job.requirements = data.get('requirements', job.requirements)
        job.location = data.get('location', job.location)
        job.school = data.get('school', job.school)
        job.level = data.get('level', job.level)
        job.status = data.get('status', job.status)
        
        db.session.commit()
        
        return jsonify({'message': 'Job post updated successfully', 'job': job.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/generate-description', methods=['POST'])
def generate_job_description():
    """Generate a comprehensive job description using AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['job_title', 'level', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        job_title = data['job_title']
        level = data['level']
        location = data['location']
        model_name = data.get('model_name', 'gemini')
        
        # Get the job description generation prompt
        prompt = PromptManager.job_description_generation_prompt(job_title, level, location)
        
        # Get the LLM model
        llm = LLMModelFactory.get_model_provider(model_name).get_model()
        
        # Generate the job description
        try:
            response = llm.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("Empty response from LLM")
        except Exception as e:
            raise RuntimeError(f"Error generating job description: {e}")
        
        # Parse the response
        try:
            job_description = TextUtility.remove_json_marker(response.text)
        except Exception as e:
            # If JSON parsing fails, return raw response
            return jsonify({
                'error': 'Failed to parse AI response',
                'raw_response': response.text,
                'parsing_error': str(e)
            }), 500
        
        return jsonify({
            'message': 'Job description generated successfully',
            'job_description': job_description,
            'input': {
                'job_title': job_title,
                'level': level,
                'location': location
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@job_bp.route('/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        job = JobPost.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({'message': 'Job post deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@job_bp.route('/<job_id>/applications', methods=['GET'])
def get_job_applications(job_id):
    try:
        job = JobPost.query.get_or_404(job_id)
        applications = job.applications
        return jsonify([application.to_dict() for application in applications]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
