#!/usr/bin/env python3

import os
from app import create_app, db

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)
# Ensure uploads directory exists
os.makedirs('uploads/resumes', exist_ok=True)

from models import (
    Role, User, JobPost, Resume, Application, Interview,
    Training, Course, Enrollment, Report, EODReport, ExpenseReport,
    PerformanceReview, Notification, AuditLog, Vacancy,
    HiringPipelineStage, CandidatePipelineStage, InterviewerAssignment, Scorecard
)

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating tables...")
        db.create_all()
        
        print("Creating basic roles...")
        roles_data = [
        {'name': 'ho', 'description': 'HO (Head Office) staff'},
        {'name': 'bda', 'description': 'Business Development Associate'},
        {'name': 'hr', 'description': 'Human Resources personnel'},
        {'name': 'candidate', 'description': 'Teacher applicant or candidate'},
    ]
        
        for role_data in roles_data:
            role = Role(**role_data)
            db.session.add(role)
        
        print("Creating default hiring pipeline stages...")
        pipeline_stages = [
            {'name': 'Shortlisted', 'description': 'Initial resume review and screening', 'order_index': 1},
            {'name': 'Technical Test', 'description': 'Technical skills assessment', 'order_index': 2},
            {'name': 'Technical Interview', 'description': 'In-depth technical interview', 'order_index': 3},
            {'name': 'Behavioral Interview', 'description': 'Behavioral and culture fit interview', 'order_index': 4},
            {'name': 'Final Interview', 'description': 'Final interview with hiring manager', 'order_index': 5},
            {'name': 'Onboarding', 'description': 'Candidate onboarding and orientation', 'order_index': 6},
            {'name': 'Offer', 'description': 'Job offer extended', 'order_index': 5},
            {'name': 'Hired', 'description': 'Candidate accepted offer and hired', 'order_index': 8}
        ]
        
        for stage_data in pipeline_stages:
            stage = HiringPipelineStage(**stage_data)
            db.session.add(stage)
        
        db.session.commit()
        
        print("Database initialized successfully!")
        print("Available roles:")
        roles = Role.query.all()
        for role in roles:
            print(f"  - {role.name}: {role.description}")
        
        print("\nDefault pipeline stages:")
        stages = HiringPipelineStage.query.order_by(HiringPipelineStage.order_index).all()
        for stage in stages:
            print(f"  {stage.order_index}. {stage.name}: {stage.description}")

if __name__ == '__main__':
    init_database()
