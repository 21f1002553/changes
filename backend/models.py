import uuid
from datetime import datetime, date
from app import db
import json

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=True)
    
    job_posts = db.relationship('JobPost', backref='posted_by', lazy=True)
    resumes = db.relationship('Resume', backref='owner', lazy=True)
    applications = db.relationship('Application', backref='candidate', lazy=True)
    interviews_as_interviewer = db.relationship('Interview', backref='interviewer', lazy=True)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    reports = db.relationship('Report', foreign_keys='Report.user_id', backref='user', lazy=True)
    approved_reports = db.relationship('Report', foreign_keys='Report.approved_by', backref='approver', lazy=True)
    employee_reviews = db.relationship('PerformanceReview', foreign_keys='PerformanceReview.employee_id', backref='employee', lazy=True)
    reviewer_reviews = db.relationship('PerformanceReview', foreign_keys='PerformanceReview.reviewer_id', backref='reviewer', lazy=True)
    notifications = db.relationship('Notification', backref='recipient', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='actor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class JobPost(db.Model):
    __tablename__ = 'job_posts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(200))
    school = db.Column(db.String(200))
    level = db.Column(db.String(100))
    posted_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='active')
    
    applications = db.relationship('Application', backref='job', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'school': self.school,
            'level': self.level,
            'posted_by_id': self.posted_by_id,
            'posted_by_name': self.posted_by.name if self.posted_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status
        }

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(500)) 
    file_url = db.Column(db.String(500))
    file_size = db.Column(db.Integer) 
    file_id = db.Column(db.String(36), db.ForeignKey('files.id'), nullable=True)  # ADD THIS
    parsed_data = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='resume', lazy=True)
    file = db.relationship('File', backref='resume', lazy=True) 
    
    def get_parsed_data(self):
        return json.loads(self.parsed_data) if self.parsed_data else {}
    
    def set_parsed_data(self, data):
        self.parsed_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else None,
            'filename': self.filename,  
            'file_url': self.file_url,
            'file_size': self.file_size,  
            'file_id': self.file_id, 
            'parsed_data': self.get_parsed_data(),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=False)
    resume_id = db.Column(db.String(36), db.ForeignKey('resumes.id'), nullable=False)
    status = db.Column(db.String(50), default='applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float)
    
    # Enhanced recruitment workflow fields
    screening_notes = db.Column(db.Text)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(100))  # how they found the job
    cover_letter = db.Column(db.Text)
    expected_salary = db.Column(db.String(100))
    availability = db.Column(db.String(200))
    
    interviews = db.relationship('Interview', backref='application', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'candidate_email': self.candidate.email if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'resume_id': self.resume_id,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'score': self.score,
            'screening_notes': self.screening_notes,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'source': self.source,
            'cover_letter': self.cover_letter,
            'expected_salary': self.expected_salary,
            'availability': self.availability
        }

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    interviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    feedback = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'interviewer_id': self.interviewer_id,
            'interviewer_name': self.interviewer.name if self.interviewer else None,
            'status': self.status,
            'feedback': self.feedback
        }

class Training(db.Model):
    __tablename__ = 'trainings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    courses = db.relationship('Course', backref='training', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    training_id = db.Column(db.String(36), db.ForeignKey('trainings.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_url = db.Column(db.String(500))
    duration_mins = db.Column(db.Integer)
    
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'training_id': self.training_id,
            'training_title': self.training.title if self.training else None,
            'title': self.title,
            'content_url': self.content_url,
            'duration_mins': self.duration_mins
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='enrolled')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'course_id': self.course_id,
            'course_title': self.course.title if self.course else None,
            'progress': self.progress,
            'status': self.status
        }
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_type = db.Column(db.String(50), nullable=False)  # eod|leave|expense|recruitment
    user_id  = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ADD THESE:
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    approval_status = db.Column(db.String(20), default='pending')  # pending|approved|rejecte
    
    # Date range
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Filters (stored as JSON)
    filters = db.Column(db.JSON)
    
    # Output
    format = db.Column(db.String(20), nullable=False)  # pdf|excel|json
    file_path = db.Column(db.String(255))  # Path to generated file
    data = db.Column(db.JSON)  # Store JSON data
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_type': self.report_type,
            'user_id': self.user_id,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'filters': self.filters,
            'format': self.format,
            'file_path': self.file_path
        }

class EODReport(db.Model):
    __tablename__ = 'eod_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    role = db.Column(db.String(20))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    
    tasks = db.Column(db.JSON)
    ai_summary = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "report_id": self.report_id,
            "role": self.role,
            "date": self.date.isoformat() if self.date else None,
            "time": str(self.time) if self.time else None,
            "tasks": self.tasks,
            "ai_summary": self.ai_summary
        }

class ExpenseReport(db.Model):
    __tablename__ = 'expense_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    items = db.Column(db.Text)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    
    def get_items(self):
        return json.loads(self.items) if self.items else []
    
    def set_items(self, items):
        self.items = json.dumps(items)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'items': self.get_items(),
            'total': self.total,
            'status': self.status
        }

class PerformanceReview(db.Model):
    __tablename__ = 'performance_reviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text)
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'type': self.type,
            'text': self.text,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.name if self.recipient else None,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.String(36), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_name': self.actor.name if self.actor else None,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class OnBoardingDocument(db.Model):
    __tablename__ = 'onboarding'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    offer_id = db.Column(db.String(36), db.ForeignKey('offer_letters.id'), nullable=True)

    employee = db.relationship('User', foreign_keys=[employee_id], backref='onboarding_documents', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'doc_type': self.doc_type,
            'filename': self.filename,
            'file_path': self.file_path,
            'verified': self.verified,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'offer_id': self.offer_id
        }
    
class OfferLetter(db.Model):
    __tablename__ = 'offer_letters'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='draft')
    acceptance_status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    filename = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    employee = db.relationship("User", foreign_keys=[employee_id], backref="offer_letters", lazy=True)
    job = db.relationship("JobPost", backref="offer_letters", lazy=True)
    documents = db.relationship("OnBoardingDocument", backref="offer", lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'filename': self.filename,
            'file_path': self.file_path,
            'status': self.status,
            'acceptance_status': self.acceptance_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }
    
class OnboardingForm(db.Model):
    __tablename__ = 'onboarding_form'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    form_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    submitted_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    signed_doc_id = db.Column(db.String(36), db.ForeignKey('onboarding.id'), nullable=True)
    employee = db.relationship("User", foreign_keys=[employee_id], backref="submitted_forms", lazy=True)
    submitted_user = db.relationship("User", foreign_keys=[submitted_by], lazy=True)
    signed_doc = db.relationship("OnBoardingDocument", foreign_keys=[signed_doc_id], lazy=True)

    def get_payload(self):
        try:
            return json.loads(self.payload)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'form_type': self.form_type,
            'payload': self.get_payload(),
            'signed_doc_id': self.signed_doc_id,
            'submitted_by': self.submitted_by,
            'submitted_by_name': self.submitted_user.name if self.submitted_user else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


# -----Leave Adjustment------
class LeaveBalance(db.Model):
    __tablename__ = 'leave_balances'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    sick_leave = db.Column(db.Integer, default=12)
    casual_leave = db.Column(db.Integer, default=8)
    lop_leave = db.Column(db.Integer, default=0)

    employee = db.relationship('User', backref='leave_balance', uselist=False)

    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'sick_leave': self.sick_leave,
            'casual_leave': self.casual_leave,
            'lop_leave': self.lop_leave,
        }

class LeaveRecord(db.Model):
    __tablename__ = 'leave_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # 'Sick', 'Casual', 'LOP'
    days = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('User', backref='leave_records')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'days': self.days,
            'date': self.date.isoformat(),
            'reason': self.reason,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'employee_name': self.employee.name if self.employee else None
        }

# -----Salary Calculations------
class SalaryRecord(db.Model):
    __tablename__ = 'salary_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    deduction = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('User', backref='salary_records')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'month': self.month,
            'year': self.year,
            'basic_salary': self.basic_salary,
            'deduction': self.deduction,
            'net_salary': self.net_salary,
            'generated_at': self.generated_at.isoformat()
        }

class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(200))
    school = db.Column(db.String(200))
    level = db.Column(db.String(100))
    department = db.Column(db.String(200))
    salary_range = db.Column(db.String(100))
    employment_type = db.Column(db.String(50), default='full-time')  # full-time, part-time, contract
    posted_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='active')
    
    # Relationship to user who posted
    posted_by = db.relationship('User', backref='vacancies', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "location": self.location,
            "school": self.school,
            "level": self.level,
            "department": self.department,
            "salary_range": self.salary_range,
            "employment_type": self.employment_type,
            "posted_by_id": self.posted_by_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_type = db.Column(db.String(50), nullable=False)  # pdf, docx, etc.
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100))  # resume, document, contract, report, etc.
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploaded_by = db.relationship('User', backref='uploaded_files', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'uploaded_by_id': self.uploaded_by_id,
            'category': self.category,
            'description': self.description,
            'is_public': self.is_public,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': self.uploaded_by.name if self.uploaded_by else None
        }


class HiringPipelineStage(db.Model):
    __tablename__ = 'hiring_pipeline_stages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate_stages = db.relationship('CandidatePipelineStage', backref='stage', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CandidatePipelineStage(db.Model):
    __tablename__ = 'candidate_pipeline_stages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=False)
    stage_id = db.Column(db.String(36), db.ForeignKey('hiring_pipeline_stages.id'), nullable=False)
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # active, completed, skipped
    notes = db.Column(db.Text)
    moved_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref='pipeline_stages', lazy=True)
    job = db.relationship('JobPost', backref='candidate_stages', lazy=True)
    moved_by = db.relationship('User', foreign_keys=[moved_by_id], lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'stage_id': self.stage_id,
            'stage_name': self.stage.name if self.stage else None,
            'entered_at': self.entered_at.isoformat() if self.entered_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'notes': self.notes,
            'moved_by_id': self.moved_by_id,
            'moved_by_name': self.moved_by.name if self.moved_by else None
        }

class InterviewerAssignment(db.Model):
    __tablename__ = 'interviewer_assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=False)
    interviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    interview_type = db.Column(db.String(50), default='technical')  # technical, hr, behavioral, final
    scheduled_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=60)
    meeting_link = db.Column(db.String(500))
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no_show
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref='interview_assignments_as_candidate', lazy=True)
    job = db.relationship('JobPost', backref='interview_assignments', lazy=True)
    interviewer = db.relationship('User', foreign_keys=[interviewer_id], backref='interview_assignments_as_interviewer', lazy=True)
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], lazy=True)
    
    # Link to scorecards
    scorecards = db.relationship('Scorecard', backref='interview_assignment', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'interviewer_id': self.interviewer_id,
            'interviewer_name': self.interviewer.name if self.interviewer else None,
            'interview_type': self.interview_type,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'duration_minutes': self.duration_minutes,
            'meeting_link': self.meeting_link,
            'status': self.status,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'assigned_by_id': self.assigned_by_id,
            'assigned_by_name': self.assigned_by.name if self.assigned_by else None
        }

class Scorecard(db.Model):
    __tablename__ = 'scorecards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_assignment_id = db.Column(db.String(36), db.ForeignKey('interviewer_assignments.id'), nullable=False)
    interviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=False)
    
    # Scoring categories
    technical_score = db.Column(db.Float)
    communication_score = db.Column(db.Float)
    problem_solving_score = db.Column(db.Float)
    cultural_fit_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    
    # Detailed feedback
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    feedback_notes = db.Column(db.Text)
    recommendation = db.Column(db.String(50))  # hire, no_hire, maybe, strong_hire
    
    # Metadata
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_final = db.Column(db.Boolean, default=False)
    
    # Relationships
    interviewer = db.relationship('User', foreign_keys=[interviewer_id], backref='scorecards_as_interviewer', lazy=True)
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref='scorecards_as_candidate', lazy=True)
    job = db.relationship('JobPost', backref='scorecards', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_assignment_id': self.interview_assignment_id,
            'interviewer_id': self.interviewer_id,
            'interviewer_name': self.interviewer.name if self.interviewer else None,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'technical_score': self.technical_score,
            'communication_score': self.communication_score,
            'problem_solving_score': self.problem_solving_score,
            'cultural_fit_score': self.cultural_fit_score,
            'overall_score': self.overall_score,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'feedback_notes': self.feedback_notes,
            'recommendation': self.recommendation,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'is_final': self.is_final
        }


class AITestAssignment(db.Model):
    __tablename__ = 'ai_test_assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey('job_posts.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False, default='ai_technical_test')
    questions = db.Column(db.Text, nullable=False)  # JSON string
    answers = db.Column(db.Text, nullable=True)  # JSON string - filled when candidate submits
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    deadline = db.Column(db.DateTime, nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, in_progress, submitted, assessed
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref='ai_tests_taken')
    job = db.relationship('JobPost', backref='ai_tests')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'test_type': self.test_type,
            'questions': self.questions,
            'answers': self.answers,
            'duration_minutes': self.duration_minutes,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'instructions': self.instructions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

class AITestAssessment(db.Model):
    __tablename__ = 'ai_test_assessments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_assignment_id = db.Column(db.String(36), db.ForeignKey('ai_test_assignments.id'), nullable=False)
    candidate_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # Overall score
    feedback = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.String(20), nullable=False)  # pass, fail, borderline
    evaluated_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    evaluated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    test_assignment = db.relationship('AITestAssignment', backref='assessments', foreign_keys=[test_assignment_id])
    candidate = db.relationship('User', foreign_keys=[candidate_id])
    evaluator = db.relationship('User', foreign_keys=[evaluated_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_assignment_id': self.test_assignment_id,
            'candidate_id': self.candidate_id,
            'score': self.score,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendation': self.recommendation,
            'evaluated_by': self.evaluated_by,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
        }


# Add to models.py

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assigned_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, reviewed
    
    # Employee self-review
    employee_review = db.Column(db.Text)
    employee_reviewed_at = db.Column(db.DateTime)
    
    # Manager review
    manager_review = db.Column(db.Text)
    manager_reviewed_at = db.Column(db.DateTime)
    
    # AI-generated summary
    ai_summary = db.Column(db.Text)
    ai_summary_generated_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks', lazy=True)
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], backref='created_tasks', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': self.assigned_to.name if self.assigned_to else None,
            'assigned_by_id': self.assigned_by_id,
            'assigned_by_name': self.assigned_by.name if self.assigned_by else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority,
            'status': self.status,
            'employee_review': self.employee_review,
            'employee_reviewed_at': self.employee_reviewed_at.isoformat() if self.employee_reviewed_at else None,
            'manager_review': self.manager_review,
            'manager_reviewed_at': self.manager_reviewed_at.isoformat() if self.manager_reviewed_at else None,
            'ai_summary': self.ai_summary,
            'ai_summary_generated_at': self.ai_summary_generated_at.isoformat() if self.ai_summary_generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        