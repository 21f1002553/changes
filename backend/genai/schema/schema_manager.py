import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


@dataclass
class RAGEngine:
    persist_dir: str = './chroma_rag_chatbot'
    collection_name: str = 'school_policies'
    temperature: float = 0.0
    k: int = 4
    search_type: str = 'similarity'
    chunk_size: int = 500
    chunk_overlap: int = 50
    glob: str = '**/*'
    separators: str = " "



# data validation class
class PerformanceReviewRequest(BaseModel):
    employee_id: str = Field(..., description="The ID of the employee to generate a performance review for.")
    reviewer_id: str = Field(..., description="The ID of the reviewer generating the performance review.")
    employee_review: str = Field(..., min_length=10, max_length=5000, description="The employee's self-assessment of their performance.")
    manager_review: str = Field(..., min_length=10, max_length=5000, description="The manager's review of the employee's performance.")


    @validator('employee_review', 'manager_review')
    def validate_review_content(cls,v):
        if not v.strip():
            raise ValueError("Review content cannot be empty.")
        return v.strip()


class ProfileEnhancementRequest(BaseModel):
    job_title: str = Field(..., description="The job title to generate profile enhancement suggestions for.")


    @validator('job_title')
    def validate_job_title(cls,v):
        if not v.strip():
            raise ValueError("Job title cannot be empty.")
        return v.strip()
    

class JobDescriptionRequest(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=200, description="Job title for JD generation")
    
    @validator('job_title')
    def validate_job_title(cls, v):
        if not v.strip():
            raise ValueError('Job title cannot be empty or whitespace only')
        return v.strip().title()


class UpskillingPathRequest(BaseModel):
    job_title: Optional[str] = Field(None, max_length=200, description="Target job title")
    job_description: Optional[str] = Field(None, max_length=2000, description="Job description")
    career_goals: Optional[str] = Field(None, max_length=1000, description="Career goals")
    
    @validator('job_title', 'career_goals')
    def validate_optional_text_fields(cls, v):
        if v and not v.strip():
            raise ValueError('Field cannot be empty if provided')
        return v.strip() if v else v
    
    @validator('job_description')
    def validate_job_description(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Job description must be at least 10 characters if provided')
        return v.strip() if v else v

class ChatbotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    context: Optional[str] = Field(None, max_length=2000, description="Additional context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()

class InterviewQuestionsQuery(BaseModel):
    n_easy_questions: Optional[int] = Field(3, ge=1, le=10, description="Number of easy questions")
    n_medium_questions: Optional[int] = Field(3, ge=1, le=10, description="Number of medium questions") 
    n_hard_questions: Optional[int] = Field(4, ge=1, le=15, description="Number of hard questions")
    
    @validator('n_easy_questions', 'n_medium_questions', 'n_hard_questions')
    def validate_question_counts(cls, v):
        if v is not None and (v < 1 or v > 15):
            raise ValueError('Question count must be between 1 and 15')
        return v


# Response Models
class PerformanceReviewResponse(BaseModel):
    performance_review: Optional[Dict]
    message: str = "Performance review generated successfully"

class ProfileEnhancementResponse(BaseModel):
    profile_enhancement: str
    message: str = "Profile enhancement suggestions generated successfully"

class JobDescriptionResponse(BaseModel):
    job_description: dict
    message: str = "Job description generated successfully"

class InterviewQuestionsResponse(BaseModel):
    interview_questions: dict
    message: str = "Interview questions generated successfully"

class UpskillingPathResponse(BaseModel):
    upskilling_path: dict
    message: str = "Upskilling path generated successfully"

class JobPostsResponse(BaseModel):
    job_posts: List[dict]
    message: str = "Job posts retrieved successfully"

class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


rag_engine=RAGEngine()