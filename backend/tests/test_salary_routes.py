import json
from datetime import datetime
from app import db
from models import User, LeaveBalance, SalaryRecord

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def create_user(
    name="Employee",
    email="emp@test.com",
    password="pass",
    role_id="default-role",
):
    user = User(
        name=name,
        email=email,
        password=password,
        role_id=role_id,
        status="active",
        email_notifications=True,
        sms_notifications=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_balance(user, sick=10, casual=10, lop=0):
    bal = LeaveBalance(
        employee_id=user.id,
        sick_leave=sick,
        casual_leave=casual,
        lop_leave=lop
    )
    db.session.add(bal)
    db.session.commit()
    return bal


def create_salary_record(user, month=None, year=None, basic=30000, deduction=0, net=None):
    if month is None:
        month = datetime.utcnow().month
    if year is None:
        year = datetime.utcnow().year
    if net is None:
        net = basic - deduction

    rec = SalaryRecord(
        employee_id=user.id,
        month=month,
        year=year,
        basic_salary=basic,
        deduction=deduction,
        net_salary=net
    )
    db.session.add(rec)
    db.session.commit()
    return rec


# ---------------------------------------------------------
# 1. CALCULATE SALARY
# ---------------------------------------------------------

def test_calculate_salary_success(client, app):
    with app.app_context():
        user = create_user()
        create_balance(user, lop=3)  # 3 lop days → deduction = 3000

        resp = client.get(f"/api/salary/calculate/{user.id}")

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200

    assert body["data"]["basic_salary"] == 30000
    assert body["data"]["lop_days"] == 3
    assert body["data"]["deduction"] == 3000
    assert body["data"]["net_salary"] == 27000


# ---------------------------------------------------------
# 2. APPLY DEDUCTION
# ---------------------------------------------------------

def test_apply_deduction_success(client, app):
    with app.app_context():
        user = create_user()
        rec = create_salary_record(user, deduction=2000, net=28000)

        payload = {
            "employee_id": user.id,
            "amount": 500,
            "reason": "Late coming"
        }

        resp = client.post("/api/salary/deduction", json=payload)

    body = resp.get_json()
    print(json.dumps(body, indent=2))
    
    assert resp.status_code == 200

    assert body["data"]["deduction_amount"] == 500
    assert body["data"]["updated_net_salary"] == 27500


def test_apply_deduction_without_salary_record(client, app):
    with app.app_context():
        user = create_user()

        payload = {
            "employee_id": user.id,
            "amount": 300
        }

        resp = client.post("/api/salary/deduction", json=payload)

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "No salary record found. Calculate salary first."


# ---------------------------------------------------------
# 3. PAYROLL SUMMARY
# ---------------------------------------------------------

def test_get_payroll_summary_success(client, app):
    with app.app_context():
        user = create_user(name="John")
        month = datetime.utcnow().month
        year = datetime.utcnow().year

        create_salary_record(user, month=month, year=year, deduction=1000, net=29000)

        resp = client.get(f"/api/salary/payroll/{month}/{year}")

    assert resp.status_code == 200
    body = resp.get_json()

    assert body["data"][0]["employee"] == "John"
    assert body["data"][0]["net_salary"] == 29000


def test_get_payroll_summary_not_found(client, app):
    with app.app_context():
        month = 1
        year = 1999

        resp = client.get(f"/api/salary/payroll/{month}/{year}")

    assert resp.status_code == 404
    assert resp.get_json()["message"] == "No payroll records found for this month/year"
