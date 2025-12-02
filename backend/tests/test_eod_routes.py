import json
import pytest
from app import db
from models import EODReport, User, Role
from datetime import datetime


# helper to create user with a role
def create_user(role_name="teacher"):
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        db.session.commit()

    user = User(
        name=f"{role_name}_user",
        email=f"{role_name}@test.com",
        password="pass",
        role_id=role.id,
        status="active"
    )
    db.session.add(user)
    db.session.commit()
    return user


# ------------------------------
#  POST /submit
# ------------------------------

def test_submit_eod_success(client, app):
    with app.app_context():
        user = create_user("teacher")

        payload = {
            "employee_id": str(user.id),
            "report_id": "report-1",
            "role": "teacher",
            "date": "2024-01-10",
            "time": "15:30",
            "data": {"task": "Lesson planning"}
        }

        resp = client.post("/api/eod/submit", json=payload)
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 201
        assert data["message"] == "EOD report submitted successfully"
        assert data["report"]["role"] == "teacher"


def test_submit_eod_missing_fields(client, app):
    resp = client.post("/api/eod/submit", json={})
    data = resp.get_json()
    print(json.dumps(data, indent=2))

    assert resp.status_code == 400
    assert "Missing required fields" in data["error"]


def test_submit_eod_invalid_date(client, app):
    with app.app_context():
        user = create_user("teacher")

        payload = {
            "employee_id": str(user.id),
            "report_id": "xyz",
            "role": "teacher",
            "date": "invalid-date",
            "time": "12:00",
            "data": {"task": "something"}
        }

        resp = client.post("/api/eod/submit", json=payload)
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 400
        assert "Invalid date format" in data["error"]


# ------------------------------
#  GET /submissions
# ------------------------------

def test_get_eod_submissions(client, app):
    with app.app_context():
        user = create_user("teacher")

        # Add sample EOD report
        report = EODReport(
            employee_id=str(user.id),
            report_id="r1",
            role="teacher",
            date=datetime(2024, 1, 1).date(),
            time=datetime.strptime("09:00", "%H:%M").time(),
            tasks={"task": "T1"}
        )
        db.session.add(report)
        db.session.commit()

        resp = client.get("/api/eod/submissions?page=1&limit=10")
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert len(data["data"]) >= 1
        assert data["pagination"]["current_page"] == 1


# ------------------------------
#  GET /submissions/<id>
# ------------------------------

def test_get_eod_by_id_success(client, app):
    with app.app_context():
        user = create_user("teacher")

        report = EODReport(
            employee_id=str(user.id),
            report_id="r2",
            role="teacher",
            date=datetime(2024, 1, 2).date(),
            time=datetime.strptime("10:00", "%H:%M").time(),
            tasks={"task": "T2"}
        )
        db.session.add(report)
        db.session.commit()

        resp = client.get(f"/api/eod/submissions/{report.id}")
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert data["id"] == report.id


def test_get_eod_by_id_not_found(client):
    resp = client.get("/api/eod/submissions/does-not-exist")
    data = resp.get_json()
    print(json.dumps(data, indent=2))

    assert resp.status_code == 404
    assert "not found" in data["error"].lower()


# ------------------------------
#  PUT /submissions/<id>
# ------------------------------

def test_update_eod_success(client, app):
    with app.app_context():
        user = create_user("teacher")

        report = EODReport(
            employee_id=str(user.id),
            report_id="r3",
            role="teacher",
            date=datetime(2024, 1, 3).date(),
            time=datetime.strptime("11:00", "%H:%M").time(),
            tasks={"task": "Old"}
        )
        db.session.add(report)
        db.session.commit()

        payload = {
            "role": "admin",
            "date": "2024-01-05",
            "time": "14:00",
            "data": {"task": "Updated"}
        }

        resp = client.put(f"/api/eod/submissions/{report.id}", json=payload)
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert data["report"]["role"] == "admin"
        assert data["report"]["tasks"]["task"] == "Updated"


# ------------------------------
#  DELETE /submissions/<id>
# ------------------------------

def test_delete_eod_success(client, app):
    with app.app_context():
        user = create_user("teacher")

        report = EODReport(
            employee_id=str(user.id),
            report_id="r4",
            role="teacher",
            date=datetime(2024, 1, 4).date(),
            time=datetime.strptime("13:00", "%H:%M").time(),
            tasks={"task": "Delete me"}
        )
        db.session.add(report)
        db.session.commit()

        resp = client.delete(f"/api/eod/submissions/{report.id}")
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert data["message"] == "EOD Report deleted"


# ------------------------------
#  GET /templates/<role>
# ------------------------------

def test_get_eod_template_success(client):
    resp = client.get("/api/eod/templates/teacher")
    data = resp.get_json()
    print(json.dumps(data, indent=2))

    assert resp.status_code == 200
    assert data["role"] == "teacher"
    assert "classes_taught" in data["template"]


def test_get_eod_template_invalid_role(client):
    resp = client.get("/api/eod/templates/invalidRole")
    data = resp.get_json()
    print(json.dumps(data, indent=2))

    assert resp.status_code == 400
    assert "Invalid role" in data["error"]
