import json
import pytest
from app import db
from flask_jwt_extended import create_access_token
from models import User, Role, Notification


# Utility to create a user with a role
def create_user_with_role(name, role_name):
    # Check if role already exists
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        db.session.commit()

    user = User(
        name=name,
        email=f"{name}@example.com",
        password="pass",
        role=role
    )

    db.session.add(user)
    db.session.commit()
    return user

def auth_headers(user):
    token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {token}"}


# -------------------------------------------------------
# GET /api/notifications/
# -------------------------------------------------------
def test_get_notifications_success(client, app):
    with app.app_context():
        user = create_user_with_role("alice", "employee")

        # Create notifications
        n1 = Notification(recipient_id=user.id, message="Hello", read=False)
        n2 = Notification(recipient_id=user.id, message="World", read=False)
        db.session.add_all([n1, n2])
        db.session.commit()

        resp = client.get("/api/notifications/", headers=auth_headers(user))
        data = resp.get_json()
        print(json.dumps(data, indent=2))
        
        assert resp.status_code == 200
        assert len(data) == 2
        assert data[0]["message"] in ["Hello", "World"]


# -------------------------------------------------------
# POST /api/notifications/mark-read/<id>
# -------------------------------------------------------
def test_mark_notification_read_success(client, app):
    with app.app_context():
        user = create_user_with_role("bob", "employee")

        notif = Notification(recipient_id=user.id, message="Test", read=False)
        db.session.add(notif)
        db.session.commit()

        resp = client.post(f"/api/notifications/mark-read/{notif.id}")
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert data["message"] == "Notification marked as read"
        assert Notification.query.get(notif.id).read is True


# -------------------------------------------------------
# POST /api/notifications/sends
# -------------------------------------------------------
def test_send_notification_success(client, app):
    with app.app_context():
        user = create_user_with_role("charlie", "employee")

        body = {
            "recipient_id": str(user.id),
            "message": "New message"
        }

        resp = client.post("/api/notifications/sends", json=body)
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 201
        assert data["notification"]["recipient_id"] == str(user.id)
        assert data["notification"]["message"] == "New message"


# -------------------------------------------------------
# GET /api/notifications/settings
# -------------------------------------------------------
def test_get_notification_settings(client, app):
    with app.app_context():
        user = create_user_with_role("david", "employee")
        user.email_notification = True
        user.sms_notification = False
        db.session.commit()

        resp = client.get("/api/notifications/settings", headers=auth_headers(user))
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert "email_notificatins" in data
        assert data["email_notificatins"] is True


# -------------------------------------------------------
# POST /api/notifications/exam  (candidate only)
# -------------------------------------------------------
def test_send_exam_notification_candidate_only(client, app):
    with app.app_context():
        candidate = create_user_with_role("eva", "candidate")

        resp = client.post("/api/notifications/exam", json={"message": "Exam time"},
                           headers=auth_headers(candidate))

        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 201
        assert data["notification"]["recipient_id"] == str(candidate.id)


def test_send_exam_notification_unauthorized(client, app):
    with app.app_context():
        hr = create_user_with_role("harry", "hr")

        resp = client.post("/api/notifications/exam", json={}, headers=auth_headers(hr))
        print(json.dumps(resp.get_json(), indent=2))

        assert resp.status_code == 401


# -------------------------------------------------------
# POST /api/notifications/exam-complete
# -------------------------------------------------------
def test_notify_hr_on_exam_complete(client, app):
    with app.app_context():
        candidate = create_user_with_role("isabel", "candidate")
        hr1 = create_user_with_role("hr1", "hr")
        hr2 = create_user_with_role("hr2", "hr")

        resp = client.post("/api/notifications/exam-complete",
                           json={"message": "done"},
                           headers=auth_headers(candidate))

        print(json.dumps(resp.get_json(), indent=2))
        assert resp.status_code == 201

        # HR should receive notifications
        notifs = Notification.query.filter(Notification.recipient_id.in_([hr1.id, hr2.id])).all()
        assert len(notifs) == 2


# -------------------------------------------------------
# GET /api/notifications/free-manager
# -------------------------------------------------------
def test_get_free_managers_success(client, app):
    with app.app_context():
        hr = create_user_with_role("john", "hr")
        manager_role = Role.query.filter_by(name="manager").first() or Role(name="manager")
        db.session.add(manager_role)
        db.session.commit()

        m1 = User(name="m1", email="m1@test.com", password="pass",
                  role=manager_role, status="active")
        m2 = User(name="m2", email="m2@test.com", password="pass",
                  role=manager_role, status="inactive")
        db.session.add_all([m1, m2])
        db.session.commit()

        resp = client.get("/api/notifications/free-manager", headers=auth_headers(hr))
        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 200
        assert len(data) == 1
        assert data[0]["name"] == "m1"


def test_get_free_managers_unauthorized(client, app):
    with app.app_context():
        emp = create_user_with_role("sam", "employee")

        resp = client.get("/api/notifications/free-manager", headers=auth_headers(emp))
        print(json.dumps(resp.get_json(), indent=2))
        
        assert resp.status_code == 401


# -------------------------------------------------------
# POST /api/notifications/notify-manager/<manager_id>
# -------------------------------------------------------
def test_notify_manager_success(client, app):
    with app.app_context():
        hr = create_user_with_role("hrboss", "hr")
        manager = create_user_with_role("manager1", "manager")
        candidate = create_user_with_role("cand1", "candidate")

        resp = client.post(f"/api/notifications/notify-manager/{manager.id}",
                           json={"candidate_id": candidate.id, "message": "Interview now"},
                           headers=auth_headers(hr))

        data = resp.get_json()
        print(json.dumps(data, indent=2))

        assert resp.status_code == 201
        assert data["notification"]["recipient_id"] == str(manager.id)
        assert data["notification"]["message"] == "Interview now"


def test_notify_manager_candidate_not_found(client, app):
    with app.app_context():
        hr = create_user_with_role("hrr", "hr")
        manager = create_user_with_role("mgr", "manager")

        resp = client.post(f"/api/notifications/notify-manager/{manager.id}",
                           json={"candidate_id": "nonexistent"},
                           headers=auth_headers(hr))

        print(json.dumps(resp.get_json(), indent=2))

        assert resp.status_code == 404
