# tests/test_screening_routes.py
import json
import pytest
import os
import tempfile
from io import BytesIO
from unittest.mock import patch, MagicMock
from app import db
from models import User, Role, Resume, JobPost, Application
from werkzeug.security import generate_password_hash


# Helper functions
def create_role(name="candidate", description="Regular candidate"):
    """Create a role in the database."""
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return role


def create_user(name, email, role_id, status="active"):
    """Create a user in the database."""
    user = User(
        name=name,
        email=email,
        password=generate_password_hash("testpass123"),
        role_id=role_id,
        status=status
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_job_post(title, description="Test job description", posted_by_id=None):
    """Create a job post in the database."""
    job = JobPost(
        title=title,
        description=description,
        requirements="Test requirements",
        location="Test Location",
        school="Test School",
        level="Junior",
        posted_by_id=posted_by_id,
        status="active"
    )
    db.session.add(job)
    db.session.commit()
    return job


def create_resume(owner_id, file_url=None, parsed_data=None):
    """Create a resume in the database."""
    resume = Resume(
        owner_id=owner_id,
        file_url=file_url or "/test/path/resume.pdf"
    )
    
    if parsed_data:
        resume.set_parsed_data(parsed_data)
    
    db.session.add(resume)
    db.session.commit()
    return resume


def create_application(candidate_id, job_id, resume_id, status="applied", score=None):
    """Create an application in the database."""
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status=status,
        score=score
    )
    db.session.add(application)
    db.session.commit()
    return application


# =========================================================
#                UPLOAD RESUME TEST CASES
# =========================================================

def test_upload_resume_success(client, app):
    """Test successful resume upload with valid file"""
    with app.app_context():
        # Create test data
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        
        # Create a test PDF file
        test_file_content = b'%PDF-1.4\ntest content'
        
        with patch('routes.screening_routes.ResumeService') as mock_service:
            mock_service.return_value.resume_service.return_value = {
                'recommended_jobs': ['job1', 'job2']
            }
            
            response = client.post(
                '/api/screening/upload-resume',
                data={
                    'user_id': user.id,
                    'resume': (BytesIO(test_file_content), 'test_resume.pdf')
                },
                content_type='multipart/form-data'
            )
        
        data = response.get_json()
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 201
        assert data['message'] == 'Resume uploaded and processed successfully'
        assert 'resume' in data
        assert 'recommended_jobs' in data


def test_upload_resume_no_file(client, app):
    """Test resume upload without file"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        
        response = client.post(
            '/api/screening/upload-resume',
            data={'user_id': user.id},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert response.get_json()['error'] == 'No resume file provided'


def test_upload_resume_missing_user_id(client):
    """Test resume upload without user_id"""
    test_file_content = b'%PDF-1.4\ntest content'
    
    response = client.post(
        '/api/screening/upload-resume',
        data={
            'resume': (BytesIO(test_file_content), 'test_resume.pdf')
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    assert response.get_json()['error'] == 'user_id is required'


def test_upload_resume_user_not_found(client):
    """Test resume upload with non-existent user"""
    test_file_content = b'%PDF-1.4\ntest content'
    
    response = client.post(
        '/api/screening/upload-resume',
        data={
            'user_id': 'non-existent-id',
            'resume': (BytesIO(test_file_content), 'test_resume.pdf')
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 404
    assert response.get_json()['error'] == 'User not found'


def test_upload_resume_empty_filename(client, app):
    """Test resume upload with empty filename"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        
        response = client.post(
            '/api/screening/upload-resume',
            data={
                'user_id': user.id,
                'resume': (BytesIO(b'test'), '')
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert response.get_json()['error'] == 'No file selected'


def test_upload_resume_invalid_file_type(client, app):
    """Test resume upload with invalid file type"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        
        response = client.post(
            '/api/screening/upload-resume',
            data={
                'user_id': user.id,
                'resume': (BytesIO(b'test content'), 'test_resume.txt')
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Invalid file type. Allowed types: pdf, docx, doc'


def test_upload_resume_ai_processing_fails(client, app):
    """Test resume upload when AI processing fails"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        
        test_file_content = b'%PDF-1.4\ntest content'
        
        with patch('routes.screening_routes.ResumeService') as mock_service:
            mock_service.side_effect = Exception("AI processing failed")
            
            response = client.post(
                '/api/screening/upload-resume',
                data={
                    'user_id': user.id,
                    'resume': (BytesIO(test_file_content), 'test_resume.pdf')
                },
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 500  # Should fail when AI service completely fails
        # The actual implementation raises an exception when ResumeService constructor fails


# =========================================================
#                SCORE CANDIDATE TEST CASES
# =========================================================

def test_score_candidate_success(client, app):
    """Test successful candidate scoring"""
    with app.app_context():
        # Create test data
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        # Create resume with parsed data
        resume_data = {
            "skills": ["Python", "JavaScript"],
            "experience": "2 years",
            "education": [{"degree": "Computer Science"}]
        }
        resume = create_resume(user.id, parsed_data=resume_data)
        
        with patch('routes.screening_routes.LLMModelFactory') as mock_factory:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = json.dumps({
                "overall_score": 85,
                "category_scores": {
                    "skills_match": 90,
                    "experience_match": 80
                },
                "recommendation": "strong_fit"
            })
            mock_model.generate_content.return_value = mock_response
            mock_factory.get_model_provider.return_value.get_model.return_value = mock_model
            
            with patch('routes.screening_routes.TextUtility.remove_json_marker') as mock_utility:
                mock_utility.return_value = {
                    "overall_score": 85,
                    "category_scores": {"skills_match": 90}
                }
                
                response = client.post(
                    '/api/screening/score-candidate',
                    json={
                        'candidate_id': user.id,
                        'job_id': job.id
                    }
                )
        
        data = response.get_json()
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        assert data['message'] == 'Candidate scored successfully'
        assert 'scoring_result' in data
        assert data['candidate_id'] == user.id
        assert data['job_id'] == job.id


def test_score_candidate_missing_fields(client):
    """Test candidate scoring with missing required fields"""
    response = client.post(
        '/api/screening/score-candidate',
        json={'candidate_id': 'test-id'}
    )
    
    assert response.status_code == 400
    assert 'job_id is required' in response.get_json()['error']


def test_score_candidate_not_found(client):
    """Test scoring non-existent candidate"""
    response = client.post(
        '/api/screening/score-candidate',
        json={
            'candidate_id': 'non-existent-candidate',
            'job_id': 'test-job-id'
        }
    )
    
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Candidate not found'


def test_score_candidate_no_resume(client, app):
    """Test scoring candidate without resume"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        response = client.post(
            '/api/screening/score-candidate',
            json={
                'candidate_id': user.id,
                'job_id': job.id
            }
        )
        
        assert response.status_code == 404
        assert response.get_json()['error'] == 'No resume found for candidate'


def test_score_candidate_job_not_found(client, app):
    """Test scoring candidate for non-existent job"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        # Create resume so we don't fail on "No resume found" first
        resume_data = {"skills": ["Python"], "experience": "2 years"}
        create_resume(user.id, parsed_data=resume_data)
        
        response = client.post(
            '/api/screening/score-candidate',
            json={
                'candidate_id': user.id,
                'job_id': 'non-existent-job'
            }
        )
        
        assert response.status_code == 404
        assert response.get_json()['error'] == 'Job not found'


def test_score_candidate_parsing_failed(client, app):
    """Test scoring candidate when resume parsing failed"""
    with app.app_context():
        role = create_role()
        user = create_user("Test User", "test@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        # Create resume with error in parsed data
        resume = create_resume(user.id, parsed_data={"error": "Parsing failed"})
        
        response = client.post(
            '/api/screening/score-candidate',
            json={
                'candidate_id': user.id,
                'job_id': job.id
            }
        )
        
        assert response.status_code == 400
        assert 'Resume parsing failed or incomplete' in response.get_json()['error']


# =========================================================
#                GET CANDIDATES TEST CASES
# =========================================================

def test_get_candidates_all(client, app):
    """Test getting all candidates"""
    with app.app_context():
        # Create test data
        role = create_role()
        user1 = create_user("Candidate 1", "candidate1@example.com", role.id)
        user2 = create_user("Candidate 2", "candidate2@example.com", role.id)
        
        # Create resumes
        resume1 = create_resume(user1.id)
        resume2 = create_resume(user2.id)
        
        response = client.get('/api/screening/candidates')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'candidates' in data
        assert 'pagination' in data
        assert len(data['candidates']) >= 2


def test_get_candidates_by_job(client, app):
    """Test getting candidates for specific job"""
    with app.app_context():
        # Create test data
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(user.id)
        application = create_application(user.id, job.id, resume.id, score=85)
        
        response = client.get(f'/api/screening/candidates?job_id={job.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['candidates']) >= 1
        assert data['filters']['job_id'] == job.id


def test_get_candidates_with_score_filter(client, app):
    """Test getting candidates with score filters"""
    with app.app_context():
        # Create test data
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(user.id)
        application = create_application(user.id, job.id, resume.id, score=85)
        
        response = client.get(f'/api/screening/candidates?job_id={job.id}&min_score=80')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['filters']['min_score'] == 80


def test_get_candidates_pagination(client, app):
    """Test candidate pagination"""
    with app.app_context():
        role = create_role()
        
        # Create multiple candidates
        for i in range(5):
            user = create_user(f"Candidate {i}", f"candidate{i}@example.com", role.id)
            create_resume(user.id)
        
        response = client.get('/api/screening/candidates?limit=2&offset=0')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['limit'] == 2
        assert data['pagination']['offset'] == 0
        assert len(data['candidates']) <= 2


# =========================================================
#            UPDATE CANDIDATE ACTION TEST CASES
# =========================================================

def test_update_candidate_action_success(client, app):
    """Test successful candidate action update"""
    with app.app_context():
        # Create test data
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(user.id)
        application = create_application(user.id, job.id, resume.id)
        
        response = client.put(
            f'/api/screening/candidates/{user.id}/action',
            json={
                'action': 'shortlist',
                'job_id': job.id,
                'notes': 'Strong candidate',
                'reviewer_id': hr_user.id
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Candidate action updated: shortlist' in data['message']
        assert data['action'] == 'shortlist'
        assert data['status_change']['to'] == 'screening'


def test_update_candidate_action_missing_action(client, app):
    """Test candidate action update without action"""
    with app.app_context():
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        
        response = client.put(
            f'/api/screening/candidates/{user.id}/action',
            json={'job_id': 'test-job'}
        )
        
        assert response.status_code == 400
        assert response.get_json()['error'] == 'action is required'


def test_update_candidate_action_invalid_action(client, app):
    """Test candidate action update with invalid action"""
    with app.app_context():
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        
        response = client.put(
            f'/api/screening/candidates/{user.id}/action',
            json={
                'action': 'invalid_action',
                'job_id': 'test-job'
            }
        )
        
        assert response.status_code == 400
        assert 'Invalid action' in response.get_json()['error']


def test_update_candidate_action_no_application(client, app):
    """Test candidate action update when application doesn't exist"""
    with app.app_context():
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        response = client.put(
            f'/api/screening/candidates/{user.id}/action',
            json={
                'action': 'shortlist',
                'job_id': job.id
            }
        )
        
        assert response.status_code == 404
        assert 'Application not found' in response.get_json()['error']


def test_update_candidate_action_without_job(client, app):
    """Test candidate action update without job context"""
    with app.app_context():
        role = create_role()
        user = create_user("Test Candidate", "candidate@example.com", role.id)
        
        response = client.put(
            f'/api/screening/candidates/{user.id}/action',
            json={
                'action': 'shortlist',
                'notes': 'General shortlisting'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Candidate action recorded: shortlist' in data['message']


# =========================================================
#              BULK SCORE CANDIDATES TEST CASES
# =========================================================

def test_bulk_score_candidates_success(client, app):
    """Test successful bulk scoring of candidates"""
    with app.app_context():
        # Create test data
        role = create_role()
        user1 = create_user("Candidate 1", "candidate1@example.com", role.id)
        user2 = create_user("Candidate 2", "candidate2@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        # Create resumes
        resume1 = create_resume(user1.id)
        resume2 = create_resume(user2.id)
        
        response = client.post(
            '/api/screening/bulk-score',
            json={
                'job_id': job.id,
                'candidate_ids': [user1.id, user2.id]
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Bulk scoring completed' in data['message']
        assert data['summary']['total_requested'] == 2
        assert len(data['results']) <= 2


def test_bulk_score_candidates_missing_job_id(client):
    """Test bulk scoring without job_id"""
    response = client.post(
        '/api/screening/bulk-score',
        json={'candidate_ids': ['id1', 'id2']}
    )
    
    assert response.status_code == 400
    assert response.get_json()['error'] == 'job_id is required'


def test_bulk_score_candidates_missing_candidate_ids(client, app):
    """Test bulk scoring without candidate_ids"""
    with app.app_context():
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        response = client.post(
            '/api/screening/bulk-score',
            json={'job_id': job.id}
        )
        
        assert response.status_code == 400
        assert response.get_json()['error'] == 'candidate_ids are required'


def test_bulk_score_candidates_job_not_found(client):
    """Test bulk scoring with non-existent job"""
    response = client.post(
        '/api/screening/bulk-score',
        json={
            'job_id': 'non-existent-job',
            'candidate_ids': ['id1', 'id2']
        }
    )
    
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Job not found'


def test_bulk_score_candidates_with_errors(client, app):
    """Test bulk scoring with some candidate errors"""
    with app.app_context():
        role = create_role()
        user1 = create_user("Valid Candidate", "valid@example.com", role.id)
        hr_role = create_role("HR", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        # Create resume for valid candidate
        resume1 = create_resume(user1.id)
        
        response = client.post(
            '/api/screening/bulk-score',
            json={
                'job_id': job.id,
                'candidate_ids': [user1.id, 'non-existent-candidate']
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['results']) >= 1  # At least one valid result
        assert len(data['errors']) >= 1   # At least one error
        assert data['summary']['total_requested'] == 2


# =========================================================
#                    HELPER TESTS
# =========================================================

def test_allowed_file_function():
    """Test the allowed_file helper function"""
    from routes.screening_routes import allowed_file
    
    assert allowed_file('resume.pdf') == True
    assert allowed_file('resume.docx') == True
    assert allowed_file('resume.doc') == True
    assert allowed_file('resume.txt') == False
    assert allowed_file('resume.jpg') == False
    assert allowed_file('resume') == False


# =========================================================
#                 INTEGRATION TESTS
# =========================================================

def test_complete_screening_workflow(client, app):
    """Test complete screening workflow from upload to action"""
    with app.app_context():
        # Setup test data
        candidate_role = create_role("candidate", "Candidate role")
        hr_role = create_role("HR", "HR role")
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        
        # Step 1: Upload resume
        test_file_content = b'%PDF-1.4\ntest content'
        
        with patch('routes.screening_routes.ResumeService') as mock_service:
            mock_service.return_value.resume_service.return_value = {
                'recommended_jobs': ['job1']
            }
            
            upload_response = client.post(
                '/api/screening/upload-resume',
                data={
                    'user_id': candidate.id,
                    'resume': (BytesIO(test_file_content), 'test_resume.pdf')
                },
                content_type='multipart/form-data'
            )
        
        assert upload_response.status_code == 201
        resume_data = upload_response.get_json()
        
        # Step 2: Score candidate
        with patch('routes.screening_routes.LLMModelFactory') as mock_factory:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = json.dumps({"overall_score": 85})
            mock_model.generate_content.return_value = mock_response
            mock_factory.get_model_provider.return_value.get_model.return_value = mock_model
            
            with patch('routes.screening_routes.TextUtility.remove_json_marker') as mock_utility:
                mock_utility.return_value = {"overall_score": 85}
                
                score_response = client.post(
                    '/api/screening/score-candidate',
                    json={
                        'candidate_id': candidate.id,
                        'job_id': job.id
                    }
                )
        
        assert score_response.status_code == 200
        
        # Create an application since the action update requires it
        resume_id = Resume.query.filter_by(owner_id=candidate.id).first().id
        create_application(candidate.id, job.id, resume_id)
        
        # Step 3: Get candidates list
        candidates_response = client.get(f'/api/screening/candidates?job_id={job.id}')
        assert candidates_response.status_code == 200
        
        # Step 4: Update candidate action
        action_response = client.put(
            f'/api/screening/candidates/{candidate.id}/action',
            json={
                'action': 'shortlist',
                'job_id': job.id,
                'notes': 'Good candidate'
            }
        )
        
        print(json.dumps(action_response.get_json(), indent=2))
        assert action_response.status_code == 200
        
        # Verify the complete workflow worked
        final_candidates = client.get(f'/api/screening/candidates?job_id={job.id}')
        assert final_candidates.status_code == 200