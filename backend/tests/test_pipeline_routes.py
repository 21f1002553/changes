# test_pipeline_routes.py
import json
from datetime import datetime, timedelta
import uuid
from app import db
from models import (
    Role, User, JobPost, HiringPipelineStage, CandidatePipelineStage,
    InterviewerAssignment, Scorecard, Application
)

# -------------------------------------------------------------
# Helper: create minimal user
# -------------------------------------------------------------
def create_user():
    user = User(
        name="Test User",
        email=str(uuid.uuid4()) + "@test.com",
        password="password",
        role_id=create_role().id,   # IMPORTANT
    )
    db.session.add(user)
    db.session.commit()  # ← this assigns user.id
    return user


def create_role():
    # Check if role already exists to avoid unique constraint violation
    role = Role.query.filter_by(name="TestRole").first()
    if not role:
        role = Role(name="TestRole")
        db.session.add(role)
        db.session.commit()
    return role

def create_job(posted_by):
    job = JobPost(
        title="Teacher",
        posted_by_id=posted_by.id
    )
    db.session.add(job)
    db.session.commit()
    return job

def create_stage(name="Screening", description="Initial review", order_index=1):
    stage = HiringPipelineStage(
        name=name,
        description=description,
        order_index=order_index
    )
    db.session.add(stage)
    db.session.commit()
    return stage

def create_assignment(candidate, interviewer, job, scheduled_at=None):
    # scheduled_at can be a datetime; default to now if not provided
    if scheduled_at is None:
        scheduled_at = datetime.utcnow()
    assignment = InterviewerAssignment(
        candidate_id=candidate.id,
        interviewer_id=interviewer.id,
        job_id=job.id,
        scheduled_at=scheduled_at
    )
    db.session.add(assignment)
    db.session.commit()
    return assignment

# -------------------------------------------------------------
# TEST: GET /pipeline/stages
# -------------------------------------------------------------
def test_get_pipeline_stages(client):
    stage = HiringPipelineStage(
        name="Screening",
        description="Initial review",
        order_index=1
    )
    db.session.add(stage)
    db.session.commit()

    res = client.get("/api/pipeline/stages")
    assert res.status_code == 200

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert data["total_stages"] == 1
    assert data["stages"][0]["name"] == "Screening"


# -------------------------------------------------------------
# TEST: POST /api/pipeline/stages
# -------------------------------------------------------------
def test_create_pipeline_stage(client):
    payload = {"name": "Interview"}

    res = client.post("/api/pipeline/stages", json=payload)
    assert res.status_code == 201

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert data["stage"]["name"] == "Interview"
    assert "id" in data["stage"]


# -------------------------------------------------------------
# TEST: GET /api/pipeline/candidates/<stage_id>
# -------------------------------------------------------------
def test_get_candidates_in_stage(client):
    
    stage = create_stage()
    user = create_user()
    job = create_job(user)
    
    app = Application(
        candidate_id=user.id,
        job_id=job.id,
        resume_id=str(uuid.uuid4())
    )
    db.session.add(app)
    db.session.commit()

    cps = CandidatePipelineStage(
        candidate_id=user.id,
        job_id=job.id,
        stage_id=stage.id
    )
    db.session.add(cps)
    db.session.commit()

    res = client.get(f"/api/pipeline/candidates/{stage.id}")
    assert res.status_code == 200

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["candidate_id"] == user.id


# -------------------------------------------------------------
# TEST: PUT /api/pipeline/candidates/<id>/move
# -------------------------------------------------------------
def test_move_candidate_in_pipeline(client):
    
    user = create_user()
    hr_user = create_user()
    job = create_job(hr_user)
    stage1 = create_stage("Applied")
    stage2 = create_stage("Screening")

    # create active candidate_stage
    cps = CandidatePipelineStage(
        candidate_id=user.id,
        job_id=job.id,
        stage_id=stage1.id
    )
    db.session.add(cps)
    db.session.commit()

    payload = {
        "stage_id": stage2.id,
        "job_id": job.id,
        "notes": "moving",
        "moved_by_id": user.id
    }

    res = client.put(f"/api/pipeline/candidates/{user.id}/move", json=payload)
    assert res.status_code == 200

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert data["new_stage"] == "Screening"
    assert data["previous_stage"] == "Applied"


# -------------------------------------------------------------
# TEST: POST /api/pipeline/assign-interviewer
# -------------------------------------------------------------
def test_assign_interviewer(client):

    candidate = create_user()
    interviewer = create_user()
    job = create_job(interviewer)

    payload = {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "interviewer_id": interviewer.id,
        "scheduled_at": datetime.utcnow().isoformat()
    }

    res = client.post("/api/pipeline/assign-interviewer", json=payload)
    assert res.status_code == 201

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert data["assignment"]["candidate_id"] == candidate.id


# -------------------------------------------------------------
# TEST: POST /api/pipeline/scorecard
# -------------------------------------------------------------
def test_create_scorecard(client):
    
    candidate = create_user()
    interviewer = create_user()
    job = create_job(interviewer)
    assignment = create_assignment(candidate, interviewer, job)

    payload = {
        "interview_assignment_id": assignment.id,
        "interviewer_id": interviewer.id,
        "technical_score": 4,
        "communication_score": 5
    }

    res = client.post("/api/pipeline/scorecard", json=payload)
    assert res.status_code == 201

    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert data["scorecard"]["overall_score"] == 4.5


# -------------------------------------------------------------
# TEST: GET /api/pipeline/scorecards
# -------------------------------------------------------------
def test_get_scorecards(client):
    # minimal: ensure route works, DB empty or with single scorecard
    res = client.get("/api/pipeline/scorecards")
    assert res.status_code == 200
    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert "scorecards" in data


# -------------------------------------------------------------
# TEST: GET /api/pipeline/interview-assignments
# -------------------------------------------------------------
def test_get_interview_assignments(client):
    res = client.get("/api/pipeline/interview-assignments")
    assert res.status_code == 200
    data = res.get_json()
    print(json.dumps(data, indent=2))
    
    assert "interview_assignments" in data


# -------------------------------------------------------------
# TEST: GET /api/pipeline/stats
# -------------------------------------------------------------
def test_get_pipeline_stats(client):
    res = client.get("/api/pipeline/stats")
    assert res.status_code == 200

    data = res.get_json()
    print(json.dumps(data, indent=2))

    assert "pipeline_stats" in data
    assert "interview_stats" in data
    assert "scorecard_stats" in data
