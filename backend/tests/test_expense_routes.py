from datetime import datetime
import json
import io
from models import User, ExpenseReport, Report
from app import db

# ------------------------------
# Helpers
# ------------------------------

def create_user(
    name="User",
    email="u@test.com",
    password="pass",
    role_id=None
):
    if role_id is None:
        # Use your system's real UUID or known role
        role_id = "default-role"   

    user = User(
        name=name,
        email=email,
        password=password,
        role_id=role_id,
        status="active",
        email_notifications=True,
        sms_notifications=True
    )

    db.session.add(user)
    db.session.commit()
    return user

def create_report(user_id):
    report = Report(
        user_id=user_id,
        report_type="expense",
        start_date=datetime.utcnow().date(),
        end_date=datetime.utcnow().date(),
        generated_at=datetime.utcnow(),
        approval_status="pending",
        format="json",
        filters={},
    )
    db.session.add(report)
    db.session.commit()
    return report


def fake_receipt():
    return (io.BytesIO(b"FakeReceiptData"), "receipt.png")


# ---------------------------------------------------------
# 1. TEST SUBMIT EXPENSE (SUCCESS)
# ---------------------------------------------------------

def test_submit_expense_success(client, app):
    with app.app_context():
        user = create_user()

        file_obj, file_name = fake_receipt()

        data = {
            "user_id": user.id,
            "trip_id": "T100",
            "category": "Food",
            "amount": "50",
            "description": "Lunch",
            "expense_date": "2025-01-01"
        }

        resp = client.post(
            "/api/expenses/submit",
            data={**data, "receipt": (file_obj, file_name)},
            content_type="multipart/form-data"
        )

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 201
    assert body["success"] is True
    assert body["data"]["status"] == "pending"
    assert body["data"]["amount"] == 50.0


# ---------------------------------------------------------
# 2. TEST GET SINGLE EXPENSE
# ---------------------------------------------------------

def test_get_expense_success(client, app):
    with app.app_context():
        user = create_user()

        # Create report + expense
        report = create_report(user.id)

        exp = ExpenseReport(report_id=report.id, total=100, status="pending")
        exp.set_items([{"category": "Travel", "amount": 100}])
        db.session.add(exp)
        db.session.commit()

        resp = client.get(f"/api/expenses/{exp.id}")

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["total"] == 100
    assert body["items"][0]["category"] == "Travel"


# ---------------------------------------------------------
# 3. APPROVE EXPENSE (SUCCESS)
# ---------------------------------------------------------

def test_approve_expense_success(client, app):
    with app.app_context():
        approver = create_user(name="Manager", email="mgr@test.com")
        user = create_user(name="User", email="user@test.com")

        report = create_report(user.id)

        exp = ExpenseReport(report_id=report.id, total=80, status="pending")
        exp.set_items([{"category": "Food", "amount": 80}])
        db.session.add(exp)
        db.session.commit()

        resp = client.put(
            f"/api/expenses/{exp.id}/approve",
            json={"approver_id": approver.id, "comments": "Looks good"}
        )

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["data"]["status"] == "approved"
    assert body["data"]["approved_by"] == "Manager"


# ---------------------------------------------------------
# 4. REJECT EXPENSE (SUCCESS)
# ---------------------------------------------------------

def test_reject_expense_success(client, app):
    with app.app_context():
        approver = create_user(name="Boss", email="boss@test.com")
        user = create_user()

        report = create_report(user.id)

        exp = ExpenseReport(report_id=report.id, total=120, status="pending")
        exp.set_items([{"category": "Travel", "amount": 120}])
        db.session.add(exp)
        db.session.commit()

        resp = client.put(
            f"/api/expenses/{exp.id}/reject",
            json={"approver_id": approver.id, "reason": "Over budget"}
        )

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["data"]["status"] == "rejected"
    assert body["data"]["reason"] == "Over budget"


# ---------------------------------------------------------
# 5. UPDATE EXPENSE ONLY IF PENDING
# ---------------------------------------------------------

def test_update_expense_success(client, app):
    with app.app_context():
        user = create_user()

        report = create_report(user.id)

        exp = ExpenseReport(report_id=report.id, total=40, status="pending")
        exp.set_items([{"category": "Food", "amount": 40}])
        db.session.add(exp)
        db.session.commit()

        new_items = [{"category": "Food", "amount": 60}]
        resp = client.put(
            f"/api/expenses/{exp.id}",
            json={"items": new_items}
        )

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert body["data"]["items"][0]["amount"] == 60
    assert body["data"]["total"] == 60


# ---------------------------------------------------------
# 6. DELETE EXPENSE ONLY IF PENDING
# ---------------------------------------------------------

def test_delete_expense_success(client, app):
    with app.app_context():
        user = create_user()

        report = create_report(user.id)

        exp = ExpenseReport(report_id=report.id, total=30, status="pending")
        exp.set_items([{"category": "Supplies", "amount": 30}])
        db.session.add(exp)
        db.session.commit()

        resp = client.delete(f"/api/expenses/{exp.id}")

        remaining = ExpenseReport.query.get(exp.id)

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200
    assert remaining is None
