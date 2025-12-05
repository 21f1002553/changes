import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from datetime import timedelta
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    # Use absolute path for SQLite database
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'hr_system.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', './uploads/receipts')
    app.config['FILES_UPLOAD_FOLDER'] = os.environ.get('FILES_UPLOAD_FOLDER', './uploads/files')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB default
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['FILES_UPLOAD_FOLDER'], exist_ok=True)
    
    # JWT Config
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'changeThisSecret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions with app
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "HR Management System API",
            "description": "A comprehensive HR Management System API with auto-generated documentation",
            "version": "1.0.0",
            "contact": {
                "name": "HR System Support",
                "email": "support@hrsystem.com"
            }
        },
        "basePath": "/api",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "tags": [
            {
                "name": "General",
                "description": "General API endpoints"
            },
            {
                "name": "Users", 
                "description": "User management endpoints"
            },
            {
                "name": "Roles",
                "description": "Role management endpoints"
            },
            {
                "name": "Files",
                "description": "File management endpoints"
            }
        ]
    }
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt = JWTManager()
    jwt.init_app(app)

    # Token Blocklist
    from routes.auth_routes import BLOCKLIST
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in BLOCKLIST
    
    
    # Import and register blueprints

    from models import (
        Role, User, JobPost, Resume, Application, Interview,
        Training, Course, Enrollment, Report, EODReport, ExpenseReport,
        PerformanceReview, Notification, AuditLog, Vacancy,
        HiringPipelineStage, CandidatePipelineStage, InterviewerAssignment, Scorecard
    )
    
    from routes.user_routes import user_bp
    from routes.role_routes import role_bp
    from routes.ai_routes import ai_bp
    Swagger(app, config=swagger_config, template=swagger_template)
    
    with app.app_context():
        # Import models after db initialization but inside app context
        from models import (
            Role, User, JobPost, Resume, Application, Interview,
            Training, Course, Enrollment, Report, EODReport, ExpenseReport,
            Vacancy, HiringPipelineStage, CandidatePipelineStage, InterviewerAssignment, Scorecard,
            PerformanceReview, Notification, AuditLog, File
        )
        
        # Register blueprints - ONLY ONCE, HERE
        from routes.user_routes import user_bp
        from routes.role_routes import role_bp
        from routes.auth_routes import auth_bp
        from routes.job_routes import job_bp
        from routes.vacancy_routes import vacancy_bp
        from routes.application_routes import application_bp
        from routes.screening_routes import screening_bp
        from routes.pipeline_routes import pipeline_bp
        from routes.eod_routes import eod_bp
        from routes.onboarding_routes import onboarding_bp
        from routes.notification_routes import notification_bp
        from routes.salary_routes import salary_bp
        from routes.leave_routes import leave_bp
        from routes.training_routes import training_bp
        from routes.reporting_routes import reports_bp
        from routes.expense_routes import expense_bp
        from routes.ai_routes import ai_bp
        from routes.file_routes import file_bp
        from routes.task_routes import task_bp

    
        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(role_bp, url_prefix='/api/roles')
        app.register_blueprint(expense_bp, url_prefix='/api/expenses')
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(job_bp, url_prefix='/api/jobs')
        app.register_blueprint(vacancy_bp, url_prefix='/api/vacancies')
        app.register_blueprint(application_bp, url_prefix='/api/applications')
        app.register_blueprint(screening_bp, url_prefix='/api/screening')
        app.register_blueprint(pipeline_bp, url_prefix='/api/pipeline')

        app.register_blueprint(eod_bp, url_prefix='/api/eod')
        app.register_blueprint(onboarding_bp, url_prefix='/api/onboarding')
        
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        app.register_blueprint(notification_bp, url_prefix='/api/notifications')

        app.register_blueprint(salary_bp, url_prefix='/api/salary')
        app.register_blueprint(leave_bp, url_prefix='/api/leave')
        app.register_blueprint(training_bp, url_prefix='/api/training')
        app.register_blueprint(file_bp, url_prefix='/api/files')
        app.register_blueprint(task_bp, url_prefix='/api/tasks')
    # Root routes
    @app.route('/')
    def hello():
        return {
            'message': 'HR Management System API',
            'version': '1.0',
            'endpoints': {
                'health': '/health',
                'users': '/api/users',
                'roles': '/api/roles',
                'expenses': '/api/expenses',
                'files': '/api/files'
            }
        }
    
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'database': 'connected',
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'files_upload_folder': app.config['FILES_UPLOAD_FOLDER']
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)