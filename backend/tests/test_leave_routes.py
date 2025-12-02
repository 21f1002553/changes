import json
from datetime import datetime
from app import db
from models import User, LeaveBalance, LeaveRecord


# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def create_user(name="User", email="u@test.com"):
    user = User(
        name=name,
        email=email,
        password="pass",
        role_id="default-role",
        status="active",
        email_notifications=True,
        sms_notifications=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_balance(user, sick=10, casual=5, lop=0):
    bal = LeaveBalance(
        employee_id=user.id,
        sick_leave=sick,
        casual_leave=casual,
        lop_leave=lop,
    )
    db.session.add(bal)
    db.session.commit()
    return bal


def create_leave_record(user, leave_type="Sick", days=2, status="Pending"):
    rec = LeaveRecord(
        employee_id=user.id,
        leave_type=leave_type,
        days=days,
        date=datetime.utcnow().date(),
        reason="test",
        status=status,
    )
    db.session.add(rec)
    db.session.commit()
    return rec


# ====================================================
# 1) TEST ADJUST LEAVE
# ====================================================

def test_adjust_leave_sick_success(client, app):
    with app.app_context():
        user = create_user()
        create_balance(user, sick=5, casual=3)

        payload = {
            "employee_id": user.id,
            "leave_type": "Sick",
            "days": 2,
            "date": "2025-01-01",
            "reason": "Flu"
        }

        resp = client.post("/api/leave/adjust", json=payload)

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["data"]["leave_balance"]["sick"] == 3
    assert body["data"]["deduction"] == 0


def test_adjust_leave_lop_success(client, app):
    with app.app_context():
        user = create_user()
        create_balance(user, lop=0)

        payload = {
            "employee_id": user.id,
            "leave_type": "LOP",
            "days": 1,
            "date": "2025-01-01"
        }

        resp = client.post("/api/leave/adjust", json=payload)

    body = resp.get_json()
    print(json.dumps(body, indent=2))

    assert resp.status_code == 200
    assert body["data"]["leave_balance"]["lop"] == 1
    assert body["data"]["deduction"] == 100  # 1 day * 100


# ====================================================
# 2) TEST GET LEAVE HISTORY
# ====================================================

def test_leave_history_filtered(client, app):
    with app.app_context():
        user = create_user()
        create_leave_record(user, "Sick", days=1)

        resp = client.get(f"/api/leave/history?employee_id={user.id}")

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["data"]) == 1
    assert body["data"][0]["leave_type"] == "Sick"


# ====================================================
# 3) TEST GET LEAVE BALANCE
# ====================================================

def test_get_leave_balance_initializes_if_missing(client, app):
    with app.app_context():
        user = create_user()

        resp = client.get(f"/api/leave/balance/{user.id}")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["leave_balance"]["sick"] == 12  # default model value
    assert body["data"]["leave_balance"]["casual"] == 8
    assert body["data"]["leave_balance"]["lop"] == 0


# ====================================================
# 4) TEST LEAVE REQUEST
# ====================================================

def test_leave_request_success(client, app):
    with app.app_context():
        user = create_user()

        payload = {
            "employee_id": user.id,
            "leave_type": "Casual",
            "days": 2,
            "start_date": "2025-02-01",
            "reason": "Vacation"
        }

        resp = client.post("/api/leave/request", json=payload)

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 201
    assert body["data"]["status"] == "Pending"


def test_leave_request_invalid_type(client, app):
    with app.app_context():
        user = create_user()

        payload = {
            "employee_id": user.id,
            "leave_type": "Unknown",
            "days": 2,
            "start_date": "2025-02-01",
        }

        resp = client.post("/api/leave/request", json=payload)

    assert resp.status_code == 400


# ====================================================
# 5) APPROVE LEAVE
# ====================================================

def test_approve_leave_success(client, app):
    with app.app_context():
        user = create_user()
        create_balance(user, sick=5)

        leave = create_leave_record(user, leave_type="Sick", days=2)

        resp = client.put(f"/api/leave/approve/{leave.id}")

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["data"]["new_balance"]["sick"] == 3


def test_approve_leave_already_processed(client, app):
    with app.app_context():
        user = create_user()
        leave = create_leave_record(user, status="Approved")

        resp = client.put(f"/api/leave/approve/{leave.id}")

    assert resp.status_code == 400


# ====================================================
# 6) REJECT LEAVE
# ====================================================

def test_reject_leave_success(client, app):
    with app.app_context():
        user = create_user()
        leave = create_leave_record(user)

        resp = client.put(f"/api/leave/reject/{leave.id}")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["status"] == "Rejected"


def test_reject_leave_already_processed(client, app):
    with app.app_context():
        user = create_user()
        leave = create_leave_record(user, status="Rejected")

        resp = client.put(f"/api/leave/reject/{leave.id}")

    assert resp.status_code == 400
