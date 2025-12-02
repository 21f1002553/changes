import json
import pytest
from unittest.mock import patch, MagicMock

# -----------------------------------------
# FIXTURE: create test client with blueprint
# -----------------------------------------
@pytest.fixture
def client(app):
    return app.test_client()

# -----------------------------------------
# SUBMIT APPLICATION TESTS
# -----------------------------------------
@pytest.mark.parametrize("missing_field", ["candidate_id", "resume_id"])
def test_submit_application_missing_required_fields(client, missing_field):
    data = {"candidate_id": 1, "resume_id": 2}
    data.pop(missing_field)
    resp = client.post('/api/applications/submit', json=data)
    print(json.dumps(resp.get_json(), indent=2))
    assert resp.status_code == 400
    assert missing_field in resp.json["error"]


def test_submit_application_missing_job_and_vacancy(client):
    resp = client.post('/api/applications/submit', json={
        "candidate_id": 1,
        "resume_id": 2
    })
    assert resp.status_code == 400
    assert "Either job_id or vacancy_id is required" in resp.json["error"]


def test_submit_application_both_job_and_vacancy(client):
    resp = client.post('/api/applications/submit', json={
        "candidate_id": 1,
        "resume_id": 2,
        "job_id": 10,
        "vacancy_id": 20
    })
    assert resp.status_code == 400
    assert "Cannot apply to both" in resp.json["error"]


@patch("routes.application_routes.User")
@patch("routes.application_routes.Resume")
def test_submit_application_candidate_not_found(mock_resume, mock_user, client):
    mock_user.query.get.return_value = None

    resp = client.post('/api/applications/submit', json={
        "candidate_id": 99,
        "resume_id": 2,
        "job_id": 10
    })
    
    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 404
    assert "Candidate not found" in resp.json["error"]


@patch("routes.application_routes.User")
@patch("routes.application_routes.Resume")
@patch("routes.application_routes.JobPost")
def test_submit_application_job_not_found(mock_job, mock_resume, mock_user, client):
    mock_user.query.get.return_value = MagicMock()
    mock_resume.query.get.return_value = MagicMock()
    mock_job.query.get.return_value = None

    resp = client.post('/api/applications/submit', json={
        "candidate_id": 1,
        "resume_id": 2,
        "job_id": 123
    })

    assert resp.status_code == 404
    assert "Job not found" in resp.json["error"]


@patch("routes.application_routes.Application")
@patch("routes.application_routes.JobPost")
@patch("routes.application_routes.Resume")
@patch("routes.application_routes.User")
@patch("routes.application_routes.db")
def test_submit_application_success(mock_db, mock_user, mock_resume, mock_job, mock_app, client):
    mock_user.query.get.return_value = MagicMock()
    mock_resume.query.get.return_value = MagicMock()
    mock_job.query.get.return_value = MagicMock()
    mock_app.query.filter_by().first.return_value = None

    new_app_instance = MagicMock()
    new_app_instance.to_dict.return_value = {"id": 1}
    mock_app.return_value = new_app_instance

    resp = client.post('/api/applications/submit', json={
        "candidate_id": 1,
        "resume_id": 2,
        "job_id": 10
    })

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 201
    assert resp.json["application"]["id"] == 1

# -----------------------------------------
# GET APPLICATIONS LIST
# -----------------------------------------
@patch("routes.application_routes.Application")
def test_get_applications_success(mock_app, client):
    fake_app = MagicMock()
    fake_app.to_dict.return_value = {"id": 1}

    mock_app.query.order_by().offset().limit().all.return_value = [fake_app]
    mock_app.query.order_by().count.return_value = 1

    resp = client.get('/api/applications/')
    
    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert len(resp.json["applications"]) == 1

# -----------------------------------------
# GET APPLICATION BY ID
# -----------------------------------------
@patch("routes.application_routes.Application")
def test_get_application_success(mock_app, client):
    mock_instance = MagicMock()
    mock_instance.to_dict.return_value = {"id": 1}
    mock_instance.resume = None
    mock_instance.job = None
    mock_instance.candidate = None

    mock_app.query.get_or_404.return_value = mock_instance

    resp = client.get('/api/applications/1')
    assert resp.status_code == 200
    assert resp.json["id"] == 1

# -----------------------------------------
# UPDATE APPLICATION STATUS
# -----------------------------------------
@patch("routes.application_routes.Application")
@patch("routes.application_routes.db")
def test_update_status_missing_status(mock_db, mock_app, client):
    mock_app.query.get_or_404.return_value = MagicMock()

    resp = client.put('/api/applications/1/status', json={})
    
    print(json.dumps(resp.get_json(), indent=2))
    assert resp.status_code == 400
    assert "Status is required" in resp.json["error"]


@patch("routes.application_routes.Application")
@patch("routes.application_routes.db")
def test_update_status_invalid_status(mock_db, mock_app, client):
    mock_app.query.get_or_404.return_value = MagicMock()

    resp = client.put('/api/applications/1/status', json={"status": "nonsense"})
    
    print(json.dumps(resp.get_json(), indent=2))
    assert resp.status_code == 400
    assert "Invalid status" in resp.json["error"]


@patch("routes.application_routes.Application")
@patch("routes.application_routes.db")
def test_update_status_success(mock_db, mock_app, client):
    instance = MagicMock(status="applied")
    instance.to_dict.return_value = {"id": 1}

    mock_app.query.get_or_404.return_value = instance

    resp = client.put('/api/applications/1/status', json={"status": "interviewed"})

    print(json.dumps(resp.get_json(), indent=2))
    assert resp.status_code == 200
    assert resp.json["status_change"]["to"] == "interviewed"

# -----------------------------------------
# BULK UPDATE STATUS
# -----------------------------------------
def test_bulk_update_missing_ids(client):
    resp = client.put('/api/applications/bulk-status', json={"status": "applied"})
    assert resp.status_code == 400


def test_bulk_update_missing_status(client):
    resp = client.put('/api/applications/bulk-status', json={"application_ids": [1, 2]})
    assert resp.status_code == 400


@patch("routes.application_routes.Application")
@patch("routes.application_routes.db")
def test_bulk_update_success(mock_db, mock_app, client):
    mock_app.query.filter().update.return_value = 2

    resp = client.put('/api/applications/bulk-status', json={
        "application_ids": [1, 2],
        "status": "rejected"
    })
    
    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert resp.json["updated_count"] == 2

# -----------------------------------------
# APPLICATION STATS
# -----------------------------------------
@patch("routes.application_routes.Application")
def test_application_stats_success(mock_app, client):
    # --- Fix applied_at comparison ---
    class FakeColumn:
        def __ge__(self, other):
            return MagicMock()

    mock_app.applied_at = FakeColumn()

    # Prepare base query mock
    mock_query = MagicMock()
    mock_app.query = mock_query

    # total_applications
    mock_query.count.return_value = 10

    # status counts → query.filter().count()
    mock_filtered = MagicMock()
    mock_filtered.count.return_value = 5
    mock_query.filter.return_value = mock_filtered

    # recent applications → query.filter().count()
    # (same object is fine)
    mock_filtered.count.return_value = 2

    resp = client.get("/api/applications/stats")

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert resp.json["total_applications"] == 10
    assert "status_breakdown" in resp.json
