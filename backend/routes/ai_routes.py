from flask import Blueprint, request, jsonify
from app import db
from models import (
    AITestAssessment, AITestAssignment, User, Role, JobPost, Resume, Application, Interview,
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
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

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

        top_resume = resume_match.resume_match(job_title, job_description, job_requirements, job_post_id)

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
@jwt_required()
def chatbot(school_id):
    """
    Chat with AI assistant about school policies.

    Args:
        school_id (str): The school ID.
        question (str): The user's question.

    Returns:
        A JSON object containing the chatbot response.
    """
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        chatbot_service = ChatbotService()
        answer = chatbot_service.chat(school_id, question)
        
        if not answer:
            return jsonify({
                'success': False,
                'error': 'Failed to generate response'
            }), 500
        
        return jsonify({
            'success': True,
            'answer': answer
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error in chatbot: {str(e)}'
        }), 500


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
        
        print("######################")
        print(output)
        return jsonify({'upskilling_path': output}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Add these new routes to your existing ai_routes.py

@ai_bp.route('/schedule-test', methods=['POST'])
def schedule_test():
    """Schedule an AI test for a candidate"""
    try:
        data = request.get_json()
        
        test_assignment = AITestAssignment(
            candidate_id=data['candidate_id'],
            job_id=data['job_id'],
            test_type=data['test_type'],
            questions=data['questions'],
            duration_minutes=data['duration_minutes'],
            deadline=datetime.fromisoformat(data['deadline']),
            instructions=data.get('instructions', ''),
            status='scheduled',
            created_by=data.get('created_by')
        )
        
        db.session.add(test_assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Test scheduled successfully',
            'test_id': test_assignment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/test/<test_id>', methods=['GET'])
@jwt_required()
def get_test_by_id(test_id):
    """Get test details for taking the test"""
    try:
        current_user_id = get_jwt_identity()
        
        test = AITestAssignment.query.get_or_404(test_id)
        
        # Verify this test belongs to the current user
        if test.candidate_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(test.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@ai_bp.route('/test-results/<test_id>', methods=['GET'])
@jwt_required()
def get_test_results(test_id):
    """Get test results for evaluation"""
    try:
        test = AITestAssignment.query.get_or_404(test_id)
        
        # Only managers and hr can view results
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        role = Role.query.filter_by(id=current_user.role_id).first()
        if (current_user.role_id == role.id) and (role.name not in ['manager', 'hr']):
            return jsonify({'error': 'Unauthorized role'}), 403
        
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        if test.status != 'submitted':
            return jsonify({'error': 'Test not submitted yet'}), 400
        
        if not test.answers:
            return jsonify({'error': 'Test answers not found'}), 404
            
        return jsonify(test.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/submit-test/<test_id>', methods=['POST'])
@jwt_required()
def submit_test(test_id):
    """Candidate submits test answers"""
    try:
        data = request.get_json()
        
        test = AITestAssignment.query.get_or_404(test_id)
        test.answers = json.dumps(data['answers'])
        test.submitted_at = datetime.utcnow()
        test.status = 'submitted'
        
        db.session.commit()
        
        return jsonify({'message': 'Test submitted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/pending-assessments', methods=['GET'])
@jwt_required()
def get_pending_assessments():
    """Get tests pending manager review"""
    try:
        pending_tests = AITestAssignment.query.filter_by(status='submitted').all()
        
        return jsonify({
            'pending_tests': [test.to_dict() for test in pending_tests]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/submit-assessment', methods=['POST'])
@jwt_required()
def submit_assessment():
    """Submit test assessment by manager"""
    try:
        data = request.get_json()
        
        # Create assessment record
        assessment = AITestAssessment(
            test_id=data['test_id'],
            candidate_id=data['candidate_id'],
            total_score=data['total_score'],
            max_score=data['max_score'],
            score_percentage=data['score_percentage'],
            recommendation=data['recommendation'],
            comments=data['comments'],
            question_scores=json.dumps(data['question_scores']),
            assessed_by=data['assessed_by']
        )
        
        db.session.add(assessment)
        
        # Update test status
        test = AITestAssignment.query.get(data['test_id'])
        test.status = 'evaluated'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assessment submitted successfully',
            'assessment_id': assessment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/save-test-progress/<test_id>', methods=['POST'])
@jwt_required()
def save_test_progress(test_id):
    """Save candidate's progress during test"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        test = AITestAssignment.query.get_or_404(test_id)
        
        # Verify authorization
        if test.candidate_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update answers
        test.answers = json.dumps(data['answers'])
        test.status = 'in_progress'
        
        db.session.commit()
        
        return jsonify({'message': 'Progress saved successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@ai_bp.route('/candidate-tests', methods=['GET'])
@jwt_required()
def get_candidate_tests():
    """Get all technical tests assigned to the current candidate"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all tests for this candidate
        tests = AITestAssignment.query.filter_by(
            candidate_id=current_user_id
        ).order_by(AITestAssignment.created_at.desc()).all()
        
        result_tests = []
        for test in tests:
            test_data = test.to_dict()
            
            # Add job title
            if test.job:
                test_data['job_title'] = test.job.title
            
            # Add assessment if exists
            assessment = AITestAssessment.query.filter_by(test_id=test.id).first()
            if assessment:
                test_data['assessment'] = {
                    'score_percentage': assessment.score_percentage,
                    'recommendation': assessment.recommendation,
                    'comments': assessment.comments
                }
            
            result_tests.append(test_data)
        
        return jsonify({
            'tests': result_tests,
            'total_count': len(result_tests)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500