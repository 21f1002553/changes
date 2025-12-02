import json
import uuid
import pytest
from app import db
from models import Role, Training, Course, Enrollment, User


# --- Helpers ------------------------------------------------------------

def create_user(role_name="employee"):
    role_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    role = Role(
        id=role_id,
        name=role_name
    )
    user = User(
        id=user_id,
        name="Test User",
        email=f"{uuid.uuid4()}@mail.com",
        password="pass",
        role_id=role_id
    )

    db.session.add(role)
    db.session.add(user)
    return user


def create_training(title="Teacher Training"):
    t = Training(
        id=str(uuid.uuid4()),
        title=title,
        description="desc"
    )
    db.session.add(t)
    return t


def create_course(training_id, title="Module 1"):
    c = Course(
        id=str(uuid.uuid4()),
        title=title,
        training_id=training_id,
        content_url="http://example.com",
        duration_mins=45
    )
    db.session.add(c)
    return c


def create_enrollment(user_id, course_id, progress=20.0, status="enrolled"):
    e = Enrollment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        course_id=course_id,
        progress=progress,
        status=status
    )
    db.session.add(e)
    return e


# --- TESTS --------------------------------------------------------------


def test_list_modules(client, app):
    with app.app_context():
        t = create_training()
        c1 = create_course(t.id, "Module A")
        c2 = create_course(t.id, "Module B")
        db.session.commit()

        resp = client.get("/api/training/modules")

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))
        
        assert body["success"] is True
        assert len(body["data"]) == 2


def test_list_modules_filter_by_training(client, app):
    with app.app_context():
        t1 = create_training("T1")
        t2 = create_training("T2")

        c1 = create_course(t1.id, "Module A")
        c2 = create_course(t2.id, "Module B")
        db.session.commit()

        resp = client.get(f"/api/training/modules?training_id={t1.id}")

        body = resp.get_json()
        print(json.dumps(body, indent=2))
        
        assert resp.status_code == 200
        assert len(body["data"]) == 1
        assert body["data"][0]["training_id"] == t1.id


def test_get_module_basic(client, app):
    with app.app_context():
        t = create_training()
        c = create_course(t.id, "Module X")
        db.session.commit()

        resp = client.get(f"/api/training/modules/{c.id}")

        body = resp.get_json()
        print(json.dumps(body, indent=2))
        
        assert resp.status_code == 200
        assert body["success"] is True
        assert body["data"]["id"] == c.id
        assert body["data"]["training_title"] == t.title


def test_get_module_with_enrollment(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        e = create_enrollment(user.id, c.id, progress=50.0)
        db.session.commit()

        resp = client.get(f"/api/training/modules/{c.id}?user_id={user.id}")

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert body["data"]["enrollment"]["progress"] == 50.0


def test_update_progress_creates_enrollment_if_missing(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        db.session.commit()

        resp = client.put(
            f"/api/training/modules/{c.id}/progress",
            json={"user_id": user.id, "progress": 40}
        )

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert body["data"]["progress"] == 40
        assert body["data"]["status"] == "enrolled"


def test_update_progress_validation_error(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        db.session.commit()

        resp = client.put(
            f"/api/training/modules/{c.id}/progress",
            json={"user_id": user.id, "progress": 200}
        )

        assert resp.status_code == 400
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert "progress must be between 0 and 100" in body["error"]


def test_update_progress_marks_completed(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        e = create_enrollment(user.id, c.id, progress=20)
        db.session.commit()

        resp = client.put(
            f"/api/training/modules/{c.id}/progress",
            json={"user_id": user.id, "progress": 100}
        )

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert body["data"]["status"] == "completed"


def test_complete_module_existing_enrollment(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        e = create_enrollment(user.id, c.id, progress=40)
        db.session.commit()

        resp = client.post(
            f"/api/training/modules/{c.id}/complete",
            json={"user_id": user.id}
        )

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert body["data"]["progress"] == 100
        assert body["data"]["status"] == "completed"


def test_complete_module_creates_enrollment_if_missing(client, app):
    with app.app_context():
        user = create_user()
        t = create_training()
        c = create_course(t.id)
        db.session.commit()

        resp = client.post(
            f"/api/training/modules/{c.id}/complete",
            json={"user_id": user.id}
        )

        assert resp.status_code == 200
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert body["data"]["progress"] == 100
        assert body["data"]["status"] == "completed"
