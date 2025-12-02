# SE Project – School HRM Solution

Software Engineering Project – Sept 2025, Team 18

---

## Problem Statement

### Problem Statement 1: HRM Solution for Schools

Design and build a **web-based Human Resource Management (HRM) System** tailored for schools and educational institutions.

The application must streamline staff hiring, management, evaluations, payroll processes, attendance tracking, and internal coordination among teachers, HR personnel, and administrators.

The system should include portals for different user roles — **Admin, HR Manager, Teacher, Finance Officer, and BDA** — each with authorized access and tailored functionality.
AI-based modules should be integrated to assist in **resume screening, job matching, automated candidate evaluation, and document summarization**.

The goal is to deliver a **real-world HRM solution** improving efficiency, transparency, and collaboration within schools.

---

## Project Structure

```
backend/                                   # Flask backend application
├── app.py                                 # Main Flask server
├── config.py                              # Environment & DB configuration
├── init_db.py                             # DB initialization script
├── models.py                              # Database models (Users, Roles, Jobs, etc.)
├── requirements.txt                       # Python dependencies
├── run.py                                 # Development entrypoint / runner
├── instance/
│   └── hr_system.db                        # SQLite (instance) database
├── chroma_db/                             # local vector DB helpers
│   └── chroma_vector_db.py
├── database/
│   └── vector_db/
│       └── chroma_vector_db.py            # Vector DB adapter (alternate location)
├── genai/                                 # GenAI-related modules
│   ├── llm_factory/
│   │   ├── llm_factory_service.py
│   │   └── llm_models/
│   │       ├── base_llm_model.py
│   │       └── llm_model_implementation.py
│   ├── prompt/
│   │   └── prompt_manager.py
│   ├── schema/
│   │   └── schema_manager.py
│   └── services/
│       ├── ai_review_service.py
│       ├── chatbot_service.py
│       ├── expense_service.py
│       ├── recommendation_service.py
│       └── resume_service.py
├── routes/                                # API route blueprints
│   ├── ai_routes.py
│   ├── auth_routes.py
│   ├── role_routes.py
│   ├── user_routes.py
│   ├── eod_routes.py
│   ├── expense_routes.py
│   ├── file_routes.py
│   ├── job_routes.py
│   ├── leave_routes.py
│   ├── notification_routes.py
│   ├── onboarding_routes.py
│   ├── reporting_routes.py
│   ├── salary_routes.py
│   └── training_routes.py
├── services/                              # Business logic modules (non-genai)
│   ├── ai_review_service.py               # (also mirrored under genai/services)
│   ├── chatbot_service.py
│   ├── expense_service.py
│   ├── recommendation_service.py
│   └── resume_service.py
├── tests/                                 # Pytest test files
│   ├── conftest.py
│   ├── test_auth_routes.py
│   └── test_expense_api.py
├── uploads/                               # Uploaded files / resumes / docs
│   └── ...
└── utils/
    ├── file_utils.py
    └── text_utility.py
```

---

# Getting Started

## Backend Setup

### 1. Go to backend directory
```bash
cd backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Initialize Database 
```bash
python init_db.py
```
### 4. Run the backend server
```bash
python run.py

```
### Testing
```bash
# Run all tests
pytest tests/test_expense_api.py -v

# Test API manually
curl http://localhost:5001/health
```
---

## Frontend Setup

### 1. Go to frontend directory
```bash
cd frontend
```

### 2. Install npm dependencies
```bash
npm install
```

### 3. Start frontend server
```bash
npm run dev
```

## Environment Variables

Create a `.env` file:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///hr_system.db
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
DATA_ROOT=your-project-location
```

---

# Demo Credentials

## Admin
- **email:** `admin@gmail.com`  
- **Password:** `admin123`

## HR Manager
- **Username:** `hr@gmail.com`  
- **Password:** `hr123456`


## Business Development (BDA)
- **Username:** `bda@gmail.com`  
- **Password:** `bda12345`

## Candidate
- **Username:** `aaa@gmail.com`  
- **Password:** `12345678`

---

# Features

## Multi-Role User System
- Admin, HR, Teacher, Finance, BDA  
- **Role-based authentication & authorization**

## Recruitment Management
- Job posting & applications  
- AI-based resume screening  
- Candidate shortlisting suggestions  

## AI Integration
- Resume parsing  
- Skill extraction  
- Job-role matching  
- Automated candidate evaluation  
- Document summarization  

## Employee Records
- Digital employee profiles  
- Leave & attendance management  

## Payroll & Finance Module
- Salary generation  
- Payslips  
- Expense tracking  
 
## Training Module  
- Academic logs  
- Announcements & tasks  

## HR Dashboard
- Employee onboarding   
- Document management 
- Analytics & reporting 

## Candidate Dashboard  
- AI Performance Mansgement  
- AI Job Recommendations & Auto Apply
- AI Upskilling & Profile Enhancement 

## Admin Panel
- System-wide control  
- User role management  
 
---

# Technology Stack

## Frontend
- Vue.js (Vue CLI)
- HTML5, CSS3, JavaScript
- Axios for API communication

## Backend
- Flask (Python)
- SQLAlchemy ORM
- RESTful APIs

## Database
- SQLite (Development)

## AI Modules
- AI/ML: Google Gemini
- Vector DB: ChromaDB
- Python: scikit-learn

## Tools & Workflow
- Git & GitHub (branching + PR workflow)
- Postman for API testing
- Swagger UI for API documentation
# changes
