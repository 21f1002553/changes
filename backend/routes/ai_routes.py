from flask import Blueprint, request, jsonify
from app import db
from models import (
    User, Role, JobPost, Resume, Application, Interview,
    Training, Course, Enrollment, Report, EODReport, ExpenseReport,
    PerformanceReview, Notification, AuditLog
)
from genai.services import (
    AIPerformanceReview, ChatbotService, ResumeService, ResumeMatch, JobService, 
    RecommendationService, InterviewService, ProfileEnhancementService, JobDescriptionService, ParseResume, UpskillingPathService
)
from genai.schema.schema_manager import (
    PerformanceReviewRequest, ProfileEnhancementRequest, JobDescriptionRequest,
     UpskillingPathRequest, ChatbotRequest,
    InterviewQuestionsQuery, PerformanceReviewResponse, ProfileEnhancementResponse,
    JobDescriptionResponse, InterviewQuestionsResponse, UpskillingPathResponse,
    JobPostsResponse, ErrorResponse
)
from utils.validation_json import validate_json, validate_uuid
import json

ai_bp = Blueprint('ai', __name__)

# ai performance review
@ai_bp.route('/performance_review', methods=['POST'])
@validate_json(PerformanceReviewRequest)
def ai_performance_review(validated_data: PerformanceReviewRequest):
    """
    Generate a performance review for an employee based on their self-assessment and manager review.

    Args:
        employee_review (str): The employee's self-assessment.
        manager_review (str): The manager's review of the employee.

    Returns:
        str: The generated performance review.
    """
    try:
        if not validate_uuid(validated_data.employee_id) or not validate_uuid(validated_data.reviewer_id):
            return jsonify({'error': 'Invalid employee or reviewer ID'}), 400
        
        employee = User.query.get(validated_data.employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        reviewer = User.query.get(validated_data.reviewer_id)
        if not reviewer:
            return jsonify({'error': 'Reviewer not found'}), 404

        ai_review_service = AIPerformanceReview()
        performance_review = ai_review_service.generate_performance_review(
            validated_data.employee_review, 
            validated_data.manager_review
        )

        performance_review = PerformanceReview(
            employee_id=str(validated_data.employee_id),
            reviewer_id=str(validated_data.reviewer_id),
            type='ai_performance_review',
            text=json.dumps(performance_review),
            rating=None
        )

        db.session.add(performance_review)
        db.session.commit()

        response = PerformanceReviewResponse(
            performance_review = performance_review.to_dict()
        )
        return jsonify(response.dict()), 200
    
    except Exception as e:
        db.session.rollback()
        error_response = ErrorResponse(
            error=f"Error generating performance review: {str(e)}"
        )
        return jsonify(error_response.dict()), 500
    


## generating interview questions for a job post
@ai_bp.route('/interview_questions/<job_post_id>', methods=['GET'])
def generate_interview_questions(job_post_id):
    """
    Generate interview questions for a given job post.
    Args:
        job_post_id: id of the job post
        job_title: title of the job post
        job_description: description of the job post
        job_requirements: requirements of the job post
        n_easy_questions: number of easy questions to generate
        n_medium_questions: number of medium questions to generate
        n_hard_questions: number of hard questions to generate
    Returns:
        A JSON object containing the generated interview questions
    """
    try:
        job_post = JobPost.query.get_or_404(job_post_id)
        job_title = job_post.title
        job_description = job_post.description
        job_requirements = job_post.requirements
        # data = request.get_json()
        # job_title = data.get('job_title')
        # job_description = data.get('job_description')
        # job_requirements = data.get('job_requirements')
        n_easy_questions = 3
        n_medium_questions = 3
        n_hard_questions = 10

        interview_service = InterviewService()

        interview_question = interview_service.generate_mock_interview(job_title, job_description, job_requirements, n_easy_questions, n_medium_questions, n_hard_questions)
        if not interview_question:
            return jsonify({'error': 'Failed to generate interview questions'}), 500
        return jsonify({'interview_questions': interview_question}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

## profile enhancement - suggestion from ai to make correction in candidate's resume
@ai_bp.route('/profile_enhancement/<resume_id>', methods=['POST'])
def profile_enhancement(resume_id):
    """
    Generate profile enhancement suggestions from AI to make corrections in candidate's resume.

    Args:
        resume_id (int): The id of the resume.
        job_title (str): The job title.

    Returns:
        A JSON object containing the generated profile enhancement suggestions.
    """
    try:
        resume = ParseResume.parse_resume_text(resume_id)
        if not resume:
            return jsonify({'error': 'Failed to parse resume'}), 500

        data = request.get_json()
        job_title = data.get('job_title')
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        profile_enhancement_service = ProfileEnhancementService()
        profile_enhancement = profile_enhancement_service.generate_profile_enhancement(resume_id, job_title)
        if not profile_enhancement:
            return jsonify({'error': 'Failed to generate profile enhancement'}), 500
        return jsonify({'profile_enhancement': profile_enhancement}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



### Make JD from job title
@ai_bp.route('/make_JD', methods=['POST'])
def make_JD():
    """
    Generate job description from job title.

    Args:
        job_title (str): The job title.

    Returns:
        A JSON object containing the generated job description.
    """
    try:
        data= request.get_json()
        job_title = data.get('job_title')
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        job_description_service = JobDescriptionService()
        job_description = job_description_service.generate_job_description(str(job_title))

        if not job_description:
            return jsonify({'error': 'Failed to generate job description'}), 500
        
        return jsonify({'job_description': job_description}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
### get resume wise score from job title 

@ai_bp.route('/get_resume_score/<job_post_id>', methods=['GET'])
def get_resume_score(job_post_id):
    """
    Get the resume score for a given job post.

    Args:
        job_post_id (int): The id of the job post.

    Returns:
        A JSON object containing the resume score.
    """
    try:
        jobpost = JobPost.query.get_or_404(job_post_id)
        job_title = jobpost.title
        job_description = jobpost.description
        job_requirements = jobpost.requirements

        resume_match = ResumeMatch()

        top_resume = resume_match.resume_match(job_title, job_description, job_requirements)

        if not top_resume:
            return jsonify({'error': 'Failed to get resume score'}), 500
        
        return jsonify({'resume_score': top_resume}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


###  get courses recommendation
@ai_bp.route('/get_courses/<resume_id>', methods=['POST'])
def get_courses(resume_id):
    """
    Get the courses recommendation for a given resume.

    Args:
        resume_id (int): The id of the resume.
        job_title (str): The job title.

    Returns:
        A JSON object containing the courses recommendation.
    """
    try:
        data = request.get_json()
        job_title = data.get('job_title')
        parsed_resume = ParseResume.parse_resume_text(resume_id)
        if not parsed_resume:
            return jsonify({'error': 'Failed to parse resume'}), 500
        
        course_recommendation = RecommendationService()
        courses=Course.query.all()
        course_details = [(course.to_dict().get('title'), course.to_dict().get('duration'), course.to_dict().get('content_url')) for course in courses]
        course_recommendation = course_recommendation.generate_course_recommendations(parsed_resume, job_title, course_details)
        if not course_recommendation:
            return jsonify({'error': 'Failed to generate course recommendation'}), 500
        
        return jsonify({'course_recommendation': course_recommendation}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


### chatbot
@ai_bp.route('/chatbot/<school_id>', methods=['POST'])
def chatbot(school_id):
    pass


### get job posts based on resume 
@ai_bp.route('/get_job_posts/<resume_id>', methods=['GET'])
def get_job_posts(resume_id):
    """
    Get job posts based on resume.

    Args:
        resume_id (int): The id of the resume.

    Returns:
        A JSON object containing the job posts.
    """
    try:
        resume_service = ResumeService()
        
        job_service = JobService()
        job_service.store_multiple_job_posts()

        job_post = resume_service.resume_service(resume_id)
        print(job_post)
        if not job_post:
            return jsonify({'error': '1. Failed to get job post'}), 500
        
        return jsonify({'job_post': job_post}), 200

    except Exception as e:
        print('error in get job posts api')
        return jsonify({'error': str(e)}), 500
        


### get upskilling path 
@ai_bp.route('/get_upskilling_path/<resume_id>', methods=['POST'])
def get_upskilling_path(resume_id):
    try:
        data=request.get_json()
        parsed_resume = ParseResume.parse_resume_text(resume_id)
        courses=Course.query.all()
        course_details = [(course.to_dict().get('id'),course.to_dict().get('title'), course.to_dict().get('duration'), course.to_dict().get('content_url')) for course in courses]
        upskilling_path = UpskillingPathService()
        output = upskilling_path.get_upskilling_path(parsed_resume, data.get('job_title'), data.get('job_description'), course_details)

        if not output:
            return jsonify({'error': 'Failed to generate upskilling path'}), 500
        
        return jsonify({'upskilling_path': output}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 