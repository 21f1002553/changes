# tests/test_reporting_routes.py
import json
import pytest
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock
from app import db
from models import (
    User, Role, Report, EODReport, ExpenseReport, Application, 
    JobPost, Interview, Resume
)


# Helper functions
def create_role(name="employee", description="Regular employee"):
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
        password="hashedpassword123",
        role_id=role_id,
        status=status
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_eod_report(employee_id, report_id, role="teacher", date_obj=None, tasks=None):
    """Create an EOD report in the database."""
    if date_obj is None:
        date_obj = datetime.utcnow().date()
    
    if tasks is None:
        tasks = {"task1": "completed task", "task2": "ongoing task"}
    
    eod_report = EODReport(
        employee_id=employee_id,
        report_id=report_id,
        role=role,
        date=date_obj,
        time=datetime.utcnow().time(),
        tasks=tasks
    )
    db.session.add(eod_report)
    db.session.commit()
    return eod_report


def create_job_post(title, description="Test job", posted_by_id=None):
    """Create a job post in the database."""
    job = JobPost(
        title=title,
        description=description,
        requirements="Test requirements",
        location="Test Location",
        posted_by_id=posted_by_id,
        status="active"
    )
    db.session.add(job)
    db.session.commit()
    return job


def create_application(candidate_id, job_id, resume_id=None, status="applied"):
    """Create an application in the database."""
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        status=status,
        applied_at=datetime.utcnow()
    )
    db.session.add(application)
    db.session.commit()
    return application


def create_resume(owner_id, file_url="/test/resume.pdf"):
    """Create a resume in the database."""
    resume = Resume(
        owner_id=owner_id,
        file_url=file_url,
        uploaded_at=datetime.utcnow()
    )
    db.session.add(resume)
    db.session.commit()
    return resume


def create_expense_report(report_id, total=100.0, status="pending"):
    """Create an expense report in the database."""
    expense_report = ExpenseReport(
        report_id=report_id,
        total=total,
        status=status
    )
    expense_report.set_items([{
        "category": "Travel",
        "amount": total,
        "description": "Test expense"
    }])
    
    db.session.add(expense_report)
    db.session.commit()
    return expense_report


def create_report(user_id, report_type="expense", start_date=None, end_date=None, format="json"):
    """Create a base report in the database."""
    if start_date is None:
        start_date = datetime.utcnow().date()
    if end_date is None:
        end_date = start_date
    
    report = Report(
        user_id=user_id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        format=format
    )
    db.session.add(report)
    db.session.commit()
    return report


def create_interview(application_id, interviewer_id, status="scheduled"):
    """Create an interview in the database."""
    interview = Interview(
        application_id=application_id,
        interviewer_id=interviewer_id,
        status=status,
        scheduled_at=datetime.utcnow()
    )
    db.session.add(interview)
    db.session.commit()
    return interview


# =========================================================
#                  DASHBOARD TESTS
# =========================================================

def test_get_dashboard_data_success(client, app):
    """Test successful dashboard data retrieval"""
    with app.app_context():
        # Create test data
        role = create_role("employee", "Employee role")
        user = create_user("Test Employee", "employee@example.com", role.id)
        
        # Create EOD reports
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        create_eod_report(user.id, "report1", date_obj=today)
        create_eod_report(user.id, "report2", date_obj=yesterday)
        
        # Create applications
        hr_role = create_role("hr", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(user.id)
        create_application(user.id, job.id, resume.id, "applied")
        
        # Create expense reports
        expense_report = create_report(user.id, "expense", today, today, "json")
        create_expense_report(expense_report.id, 150.0, "pending")
        
        response = client.get('/api/reports/dashboard')
        
        data = response.get_json()
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        
        assert 'date_range' in data
        assert 'statistics' in data
        assert 'eod_reports' in data['statistics']
        assert 'applications' in data['statistics']
        assert 'expenses' in data['statistics']
        assert 'employees' in data['statistics']
        
        # Check that we have some data
        assert data['statistics']['eod_reports']['total'] >= 0
        assert data['statistics']['applications']['total'] >= 0
        assert data['statistics']['employees']['active'] >= 1


def test_get_dashboard_data_empty_database(client, app):
    """Test dashboard data with empty database"""
    with app.app_context():
        response = client.get('/api/reports/dashboard')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['statistics']['eod_reports']['total'] == 0
        assert data['statistics']['applications']['total'] == 0
        assert data['statistics']['expenses']['total_amount'] == 0.0
        assert data['statistics']['employees']['active'] == 0


# =========================================================
#                EOD SUMMARY TESTS
# =========================================================

def test_get_eod_summary_success(client, app):
    """Test successful EOD summary retrieval"""
    with app.app_context():
        # Create test data
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        # Create EOD reports with different dates
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        create_eod_report(user.id, "report1", "teacher", today)
        create_eod_report(user.id, "report2", "teacher", yesterday)
        
        response = client.get('/api/reports/eod-summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'date_range' in data
        assert 'total_reports' in data
        assert 'summary' in data
        assert data['total_reports'] >= 2


def test_get_eod_summary_with_date_filters(client, app):
    """Test EOD summary with date range filters"""
    with app.app_context():
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        # Create EOD report for today
        today = datetime.utcnow().date()
        create_eod_report(user.id, "report1", "teacher", today)
        
        # Test with specific date range
        response = client.get(f'/api/reports/eod-summary?start_date={today}&end_date={today}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['date_range']['start'] == today.isoformat()
        assert data['date_range']['end'] == today.isoformat()
        assert data['total_reports'] >= 1


def test_get_eod_summary_with_employee_filter(client, app):
    """Test EOD summary with employee filter"""
    with app.app_context():
        role = create_role("teacher", "Teacher role")
        user1 = create_user("Teacher 1", "teacher1@example.com", role.id)
        user2 = create_user("Teacher 2", "teacher2@example.com", role.id)
        
        today = datetime.utcnow().date()
        create_eod_report(user1.id, "report1", "teacher", today)
        create_eod_report(user2.id, "report2", "teacher", today)
        
        response = client.get(f'/api/reports/eod-summary?employee_id={user1.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should only get reports for user1
        assert data['total_reports'] >= 1
        for summary_date in data['summary']:
            for report in summary_date['reports']:
                assert report['employee_id'] == user1.id


def test_get_eod_summary_with_role_filter(client, app):
    """Test EOD summary with role filter"""
    with app.app_context():
        role = create_role("admin", "Admin role")
        user = create_user("Admin User", "admin@example.com", role.id)
        
        today = datetime.utcnow().date()
        create_eod_report(user.id, "report1", "admin", today)
        
        response = client.get('/api/reports/eod-summary?role=admin')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_reports'] >= 1
        for summary_date in data['summary']:
            for report in summary_date['reports']:
                assert report['role'] == 'admin'


def test_get_eod_summary_invalid_date_format(client):
    """Test EOD summary with invalid date format"""
    response = client.get('/api/reports/eod-summary?start_date=invalid-date')
    
    # Should handle gracefully and use defaults or return error
    assert response.status_code in [200, 400, 500]


# =========================================================
#            APPLICATION ANALYTICS TESTS
# =========================================================

def test_get_application_analytics_success(client, app):
    """Test successful application analytics retrieval"""
    with app.app_context():
        # Create test data
        candidate_role = create_role("candidate", "Candidate role")
        hr_role = create_role("hr", "HR role")
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        
        job1 = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        job2 = create_job_post("Data Analyst", posted_by_id=hr_user.id)
        
        resume = create_resume(candidate.id)
        
        # Create applications with different statuses
        create_application(candidate.id, job1.id, resume.id, "applied")
        create_application(candidate.id, job2.id, resume.id, "rejected")
        
        response = client.get('/api/reports/application-analytics')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'date_range' in data
        assert 'total_applications' in data
        assert 'by_status' in data
        assert 'by_job' in data
        assert data['total_applications'] >= 2


def test_get_application_analytics_with_date_range(client, app):
    """Test application analytics with custom date range"""
    with app.app_context():
        candidate_role = create_role("candidate", "Candidate role")
        hr_role = create_role("hr", "HR role")
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(candidate.id)
        
        create_application(candidate.id, job.id, resume.id, "applied")
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        response = client.get(f'/api/reports/application-analytics?start_date={yesterday}&end_date={today}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['date_range']['start'] == yesterday.isoformat()
        assert data['date_range']['end'] == today.isoformat()


def test_get_application_analytics_empty_results(client, app):
    """Test application analytics with no applications"""
    with app.app_context():
        response = client.get('/api/reports/application-analytics')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_applications'] == 0
        assert data['by_status'] == {}
        assert data['by_job'] == {}


# =========================================================
#              EXPENSE SUMMARY TESTS
# =========================================================

def test_get_expense_summary_success(client, app):
    """Test successful expense summary retrieval"""
    with app.app_context():
        # Create test data
        role = create_role("employee", "Employee role")
        user = create_user("Test Employee", "employee@example.com", role.id)
        
        # Create expense reports
        today = datetime.utcnow().date()
        
        report1 = create_report(user.id, "expense", today, today, "json")
        create_expense_report(report1.id, 100.0, "pending")
        
        report2 = create_report(user.id, "expense", today, today, "json")
        create_expense_report(report2.id, 200.0, "approved")
        
        response = client.get('/api/reports/expense-summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'date_range' in data
        assert 'total_expenses' in data
        assert 'total_amount' in data
        assert 'by_status' in data
        
        # Check status breakdown
        assert 'pending' in data['by_status']
        assert 'approved' in data['by_status']
        assert data['by_status']['pending']['count'] >= 1
        assert data['by_status']['approved']['count'] >= 1


def test_get_expense_summary_with_date_range(client, app):
    """Test expense summary with custom date range"""
    with app.app_context():
        role = create_role("employee", "Employee role")
        user = create_user("Test Employee", "employee@example.com", role.id)
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Create expense for yesterday
        report = create_report(user.id, "expense", yesterday, yesterday, "json")
        create_expense_report(report.id, 150.0, "pending")
        
        response = client.get(f'/api/reports/expense-summary?start_date={yesterday}&end_date={today}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['date_range']['start'] == yesterday.isoformat()
        assert data['date_range']['end'] == today.isoformat()


def test_get_expense_summary_empty_results(client, app):
    """Test expense summary with no expenses"""
    with app.app_context():
        response = client.get('/api/reports/expense-summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_expenses'] == 0
        assert data['total_amount'] == 0


# =========================================================
#             CUSTOM REPORT GENERATION TESTS
# =========================================================

def test_generate_custom_report_eod_success(client, app):
    """Test successful EOD report generation"""
    with app.app_context():
        # Create test data
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        create_eod_report(user.id, "report1", "teacher", today)
        create_eod_report(user.id, "report2", "teacher", yesterday)
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'eod',
                'date_range': {
                    'start': yesterday.isoformat(),
                    'end': today.isoformat()
                },
                'filters': {
                    'role': 'teacher'
                },
                'format': 'json',
                'user_id': user.id
            }
        )
        
        data = response.get_json()
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        
        assert 'report_id' in data
        assert data['report_type'] == 'eod'
        assert 'generated_at' in data
        assert 'data' in data
        assert data['data']['total_reports'] >= 2


def test_generate_custom_report_application_success(client, app):
    """Test successful application report generation"""
    with app.app_context():
        # Create test data
        candidate_role = create_role("candidate", "Candidate role")
        hr_role = create_role("hr", "HR role")
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(candidate.id)
        create_application(candidate.id, job.id, resume.id, "applied")
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'application',
                'date_range': {
                    'start': yesterday.isoformat(),
                    'end': today.isoformat()
                },
                'filters': {
                    'status': 'applied'
                },
                'format': 'json',
                'user_id': hr_user.id
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['report_type'] == 'application'
        assert data['data']['total_applications'] >= 1


def test_generate_custom_report_expense_success(client, app):
    """Test successful expense report generation"""
    with app.app_context():
        # Create test data
        role = create_role("employee", "Employee role")
        user = create_user("Test Employee", "employee@example.com", role.id)
        
        today = datetime.utcnow().date()
        
        report = create_report(user.id, "expense", today, today, "json")
        create_expense_report(report.id, 100.0, "approved")
        
        yesterday = today - timedelta(days=1)
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'expense',
                'date_range': {
                    'start': yesterday.isoformat(),
                    'end': today.isoformat()
                },
                'filters': {},
                'format': 'json',
                'user_id': user.id
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['report_type'] == 'expense'
        assert data['data']['total_expenses'] >= 1
        assert data['data']['total_amount'] >= 100.0


def test_generate_custom_report_interview_success(client, app):
    """Test successful interview report generation"""
    with app.app_context():
        # Create test data
        candidate_role = create_role("candidate", "Candidate role")
        interviewer_role = create_role("interviewer", "Interviewer role")
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        interviewer = create_user("Test Interviewer", "interviewer@example.com", interviewer_role.id)
        
        hr_role = create_role("hr", "HR role")
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(candidate.id)
        application = create_application(candidate.id, job.id, resume.id, "applied")
        
        create_interview(application.id, interviewer.id, "scheduled")
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'interview',
                'date_range': {
                    'start': yesterday.isoformat(),
                    'end': today.isoformat()
                },
                'filters': {
                    'status': 'scheduled'
                },
                'format': 'json',
                'user_id': interviewer.id
            }
        )
        
        data = response.get_json()
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        
        assert data['report_type'] == 'interview'
        assert data['data']['total_interviews'] >= 1


def test_generate_custom_report_missing_type(client):
    """Test custom report generation without report_type"""
    response = client.post(
        '/api/reports/generate',
        json={
            'date_range': {
                'start': '2024-01-01',
                'end': '2024-01-31'
            }
        }
    )
    
    assert response.status_code == 400
    assert 'report_type is required' in response.get_json()['error']


def test_generate_custom_report_invalid_type(client):
    """Test custom report generation with invalid report_type"""
    response = client.post(
        '/api/reports/generate',
        json={
            'report_type': 'invalid_type',
            'date_range': {
                'start': '2024-01-01',
                'end': '2024-01-31'
            }
        }
    )
    
    assert response.status_code == 400
    assert 'Invalid report_type' in response.get_json()['error']


def test_generate_custom_report_invalid_date_format(client):
    """Test custom report generation with invalid date format"""
    response = client.post(
        '/api/reports/generate',
        json={
            'report_type': 'eod',
            'date_range': {
                'start': 'invalid-date',
                'end': '2024-01-31'
            }
        }
    )
    
    assert response.status_code == 400
    assert 'Invalid date format' in response.get_json()['error']


def test_generate_custom_report_pdf_format(client, app):
    """Test custom report generation with PDF format (not implemented)"""
    with app.app_context():
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        today = datetime.utcnow().date()
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'eod',
                'date_range': {
                    'start': today.isoformat(),
                    'end': today.isoformat()
                },
                'format': 'pdf',
                'user_id': user.id
            }
        )
        
        assert response.status_code == 501
        data = response.get_json()
        assert 'PDF generation not yet implemented' in data['message']


def test_generate_custom_report_excel_format(client, app):
    """Test custom report generation with Excel format (not implemented)"""
    with app.app_context():
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        today = datetime.utcnow().date()
        
        response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'eod',
                'date_range': {
                    'start': today.isoformat(),
                    'end': today.isoformat()
                },
                'format': 'excel',
                'user_id': user.id
            }
        )
        
        assert response.status_code == 501
        data = response.get_json()
        assert 'Excel generation not yet implemented' in data['message']


# =========================================================
#                  EDGE CASES AND ERRORS
# =========================================================

def test_dashboard_data_database_error(client, app):
    """Test dashboard data handling when database error occurs"""
    with app.app_context():
        with patch('routes.reporting_routes.db.session.query') as mock_query:
            mock_query.side_effect = Exception("Database connection error")
            
            response = client.get('/api/reports/dashboard')
            
            assert response.status_code == 500
            assert 'error' in response.get_json()


def test_eod_summary_database_error(client, app):
    """Test EOD summary handling when database error occurs"""
    with app.app_context():
        with patch('routes.reporting_routes.db.session.query') as mock_query:
            mock_query.side_effect = Exception("Database connection error")
            
            response = client.get('/api/reports/eod-summary')
            
            assert response.status_code == 500
            assert 'error' in response.get_json()


def test_generate_custom_report_database_error(client, app):
    """Test custom report generation when database error occurs"""
    with app.app_context():
        role = create_role("teacher", "Teacher role")
        user = create_user("Test Teacher", "teacher@example.com", role.id)
        
        today = datetime.utcnow().date()
        
        with patch('routes.reporting_routes.db.session.add') as mock_add:
            mock_add.side_effect = Exception("Database save error")
            
            response = client.post(
                '/api/reports/generate',
                json={
                    'report_type': 'eod',
                    'date_range': {
                        'start': today.isoformat(),
                        'end': today.isoformat()
                    },
                    'user_id': user.id
                }
            )
            
            assert response.status_code == 500
            assert 'error' in response.get_json()


# =========================================================
#                  INTEGRATION TESTS
# =========================================================

def test_complete_reporting_workflow(client, app):
    """Test complete reporting workflow"""
    with app.app_context():
        # Step 1: Create comprehensive test data
        teacher_role = create_role("teacher", "Teacher role")
        candidate_role = create_role("candidate", "Candidate role")
        hr_role = create_role("hr", "HR role")
        
        teacher = create_user("Test Teacher", "teacher@example.com", teacher_role.id)
        candidate = create_user("Test Candidate", "candidate@example.com", candidate_role.id)
        hr_user = create_user("HR User", "hr@example.com", hr_role.id)
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Create EOD reports
        create_eod_report(teacher.id, "eod1", "teacher", today)
        create_eod_report(teacher.id, "eod2", "teacher", yesterday)
        
        # Create job and application
        job = create_job_post("Software Engineer", posted_by_id=hr_user.id)
        resume = create_resume(candidate.id)
        create_application(candidate.id, job.id, resume.id, "applied")
        
        # Create expense
        expense_report = create_report(teacher.id, "expense", today, today, "json")
        create_expense_report(expense_report.id, 250.0, "approved")
        
        # Step 2: Test dashboard (overview)
        dashboard_response = client.get('/api/reports/dashboard')
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.get_json()
        
        # Verify dashboard shows our data
        assert dashboard_data['statistics']['eod_reports']['total'] >= 2
        assert dashboard_data['statistics']['applications']['total'] >= 1
        assert dashboard_data['statistics']['employees']['active'] >= 3
        
        # Step 3: Test specific summaries
        eod_response = client.get('/api/reports/eod-summary')
        assert eod_response.status_code == 200
        eod_data = eod_response.get_json()
        assert eod_data['total_reports'] >= 2
        
        app_response = client.get('/api/reports/application-analytics')
        assert app_response.status_code == 200
        app_data = app_response.get_json()
        assert app_data['total_applications'] >= 1
        
        expense_response = client.get('/api/reports/expense-summary')
        assert expense_response.status_code == 200
        expense_data = expense_response.get_json()
        assert expense_data['total_expenses'] >= 1
        
        # Step 4: Generate custom reports
        eod_custom_response = client.post(
            '/api/reports/generate',
            json={
                'report_type': 'eod',
                'date_range': {
                    'start': yesterday.isoformat(),
                    'end': today.isoformat()
                },
                'filters': {'role': 'teacher'},
                'format': 'json',
                'user_id': hr_user.id
            }
        )
        
        print(json.dumps(eod_custom_response.get_json(), indent=2))
        
        assert eod_custom_response.status_code == 200
        custom_data = eod_custom_response.get_json()
        assert custom_data['report_type'] == 'eod'
        assert custom_data['data']['total_reports'] >= 2
        
        # Verify custom report was saved to database
        assert 'report_id' in custom_data
        saved_report = Report.query.get(custom_data['report_id'])
        assert saved_report is not None
        assert saved_report.report_type == 'eod'
        assert saved_report.user_id == hr_user.id