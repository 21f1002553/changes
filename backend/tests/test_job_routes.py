import json
import pytest
from unittest.mock import patch, MagicMock
from models import JobPost


# ---------------------------------------------------------
# Helper method to create JobPost instances
# ---------------------------------------------------------
def make_job(
    id=1,
    title="Sample Job",
    posted_by_id=1,
    description="Sample Description",
    level="Mid",
    location="Remote",
    status="open",
    school="Engineering",
    requirements="Skill A, Skill B",
    created_at="2025-01-01",
    posted_by_name="Admin"
):
    job = JobPost(
        id=id,
        title=title,
        posted_by_id=posted_by_id
    )

    # For attributes not present in the constructor, assign them manually
    job.description = description
    job.level = level
    job.location = location
    job.status = status
    job.school = school
    job.requirements = requirements
    job.created_at = created_at
    job.posted_by_name = posted_by_name

    # Mock to_dict to return ALL fields
    job.to_dict = lambda: {
        "id": id,
        "title": title,
        "posted_by_id": posted_by_id,
        "description": description,
        "level": level,
        "location": location,
        "status": status,
        "school": school,
        "requirements": requirements,
        "created_at": created_at,
        "posted_by_name": posted_by_name
    }

    return job

# ---------------------------------------------------------
# GET /api/jobs/
# ---------------------------------------------------------
def test_get_jobs(client):
    job1 = make_job(id=1, title="Job A")
    job2 = make_job(id=2, title="Job B")

    with patch("routes.job_routes.JobPost.query") as mock_query:
        mock_query.all.return_value = [job1, job2]

        response = client.get("/api/jobs/")
        assert response.status_code == 200

        data = response.get_json()
        
        print("GET /api/jobs/ response:")
        print(json.dumps(data, indent=2))
        
        assert len(data) == 2
        assert data[0]["title"] == "Job A"
        assert data[1]["title"] == "Job B"


# ---------------------------------------------------------
# GET /api/jobs/<id>
# ---------------------------------------------------------
def test_get_job_by_id(client):
    job = make_job(id=1, title="Test Job")
    with patch("routes.job_routes.JobPost.query") as mock_query:
        mock_query.get_or_404.return_value = job

        response = client.get("/api/jobs/1")
        assert response.status_code == 200
        print("GET /api/jobs/1 response:")
        print(json.dumps(response.get_json(), indent=2))        
        assert response.get_json()["title"] == "Test Job"

# ---------------------------------------------------------
# POST /api/jobs/
# ---------------------------------------------------------
def test_create_job(client):
    payload = {
        "title": "New Job",
        "posted_by_id": 1
    }

    job_instance = make_job(title="New Job")

    with (
        patch("routes.job_routes.db.session") as mock_db,
        patch("routes.job_routes.JobPost") as mock_job_model
    ):
        mock_job_model.return_value = job_instance

        response = client.post("/api/jobs/", json=payload)
        assert response.status_code == 201

        data = response.get_json()
        
        print("POST /api/jobs/ response:")
        print(json.dumps(data, indent=2))
        
        assert data["job"]["title"] == "New Job"

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


# ---------------------------------------------------------
# PUT /api/jobs/<id>
# ---------------------------------------------------------
def test_update_job(client):
    job = make_job(id=1, title="Updated Title")

    payload = {"title": "Updated Title"}

    with (
        patch("routes.job_routes.db.session") as mock_db,
        patch("routes.job_routes.JobPost.query") as mock_query
    ):
        mock_query.get_or_404.return_value = job

        response = client.put("/api/jobs/1", json=payload)
        
        data = response.get_json()
        print("PUT /api/jobs/1 response:")
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        assert data["job"]["title"] == "Updated Title"
        mock_db.commit.assert_called_once()


# ---------------------------------------------------------
# DELETE /api/jobs/<id>
# ---------------------------------------------------------
def test_delete_job(client):
    job = JobPost(id=1, title="Delete Me", posted_by_id=1)

    with (
        patch("routes.job_routes.db.session") as mock_db,
        patch("routes.job_routes.JobPost.query") as mock_query
    ):
        mock_query.get_or_404.return_value = job

        response = client.delete("/api/jobs/1")
        data = response.get_json()
        
        print("DELETE /api/jobs/1 response:")
        print(json.dumps(data, indent=2))
        
        assert response.status_code == 200
        assert data["message"] == "Job post deleted successfully"
        mock_db.delete.assert_called_once_with(job)
        mock_db.commit.assert_called_once()


# ---------------------------------------------------------
# GET /api/jobs/<id>/applications
# ---------------------------------------------------------
def test_get_job_applications(client):
    mock_application = MagicMock()
    mock_application.to_dict.return_value = {"id": 1, "applicant": "User X"}

    job = MagicMock()
    job.applications = [mock_application]

    with patch("routes.job_routes.JobPost.query") as mock_query:
        mock_query.get_or_404.return_value = job

        response = client.get("/api/jobs/1/applications")
        
        data = response.get_json()
        print("GET /api/jobs/1/applications response:")
        print(json.dumps(data, indent=2))

        assert response.status_code == 200
        assert data[0]["applicant"] == "User X"

# ---------------------------------------------------------
# POST /api/jobs/generate-description
# ---------------------------------------------------------
def test_generate_job_description(client):
    payload = {
        "job_title": "Software Engineer",
        "level": "Senior",
        "location": "Remote",
        "model_name": "gemini"
    }

    with (
        patch("routes.job_routes.PromptManager") as mock_prompt,
        patch("routes.job_routes.LLMModelFactory") as mock_llm_factory,
        patch("routes.job_routes.TextUtility") as mock_text_util
    ):
        mock_prompt.job_description_generation_prompt.return_value = "mock prompt"

        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "Generated Description"

        mock_provider = MagicMock()
        mock_provider.get_model.return_value = mock_model
        mock_llm_factory.get_model_provider.return_value = mock_provider

        mock_text_util.remove_json_marker.return_value = "Cleaned Description"

        response = client.post("/api/jobs/generate-description", json=payload)
        
        data = response.get_json()
        print("POST /api/jobs/generate-description response:")
        print(json.dumps(data, indent=2))

        assert response.status_code == 200
        assert data["job_description"] == "Cleaned Description"

# ---------------------------------------------------------
# Missing field validation (400)
# ---------------------------------------------------------
@pytest.mark.parametrize("missing_field", ["job_title", "level", "location"])
def test_generate_description_missing_fields(client, missing_field):
    payload = {
        "job_title": "X",
        "level": "Y",
        "location": "Z",
        "model_name": "gemini"
    }

    payload[missing_field] = ""

    response = client.post("/api/jobs/generate-description", json=payload)

    print("POST /api/jobs/generate-description (missing field) response:")
    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 400
    assert missing_field in response.get_json()["error"]
