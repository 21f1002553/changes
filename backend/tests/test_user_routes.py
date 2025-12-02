import pytest, json
from app import db
from models import User, Role
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def create_role(name="Employee", description="Standard"):
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return role


def create_user(name, email, password, role, status="active"):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role=role,
        status=status,
    )
    db.session.add(user)
    db.session.commit()
    return user


def auth_header(user):
    token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {token}"}


# =========================================================
# GET ALL USERS
# =========================================================

def test_get_users_admin_success(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        candidate_role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)
        u1 = create_user("U1", "u1@test.com", "pass", candidate_role)
        u2 = create_user("U2", "u2@test.com", "pass", candidate_role)

        response = client.get("/api/users/", headers=auth_header(admin))

    print("\n[RESPONSE]", json.dumps(response.get_json(), indent=2))

    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_get_users_candidate_sees_only_self(client, app):
    with app.app_context():
        role = create_role("candidate")
        user = create_user("C", "c@test.com", "pass", role)
        user2 = create_user("C2", "c2@test.com", "pass", role)
        user3 = create_user("C3", "c3@test.com", "pass", role)

        response = client.get("/api/users/", headers=auth_header(user))

    users = response.get_json()
    assert response.status_code == 200
    assert len(users) == 1
    assert users[0]["email"] == "c@test.com"


# =========================================================
# CREATE USER
# =========================================================

def test_create_user_admin_success(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        candidate_role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)

        payload = {
            "name": "New User",
            "email": "new@test.com",
            "role_id": candidate_role.id,
        }

        response = client.post("/api/users/", json=payload, headers=auth_header(admin))

    print("\n[RESPONSE]")
    print(json.dumps(response.get_json(), indent=2))
    
    assert response.status_code == 201
    assert response.get_json()["user"]["email"] == "new@test.com"


def test_create_user_non_admin_forbidden(client, app):
    with app.app_context():
        role1 = create_role("manager")
        role2 = create_role("bda")
        role3 = create_role("hr")
        role4 = create_role("Interviewer")
        candidate_role = create_role("candidate")
        
        user1 = create_user("Manager", "manager@test.com", "pass", role1)
        user2 = create_user("BDA", "bda@test.com", "pass", role2)
        user3 = create_user("HR", "hr@test.com", "pass", role3)
        user4 = create_user("Interviewer", "interviewer@test.com", "pass", role4)
        
        # Create separate payloads with different emails
        payload1 = {
            "name": "New User",
            "email": "new@test.com",
            "role_id": candidate_role.id,
        }
        
        payload2 = {
            "name": "New User",
            "email": "new2@test.com",
            "role_id": candidate_role.id,
        }
        
        payload3 = {
            "name": "New User",
            "email": "new3@test.com",
            "role_id": candidate_role.id,
        }
        
        payload4 = {
            "name": "New User",
            "email": "new4@test.com",
            "role_id": candidate_role.id,
        }

        response1 = client.post("/api/users/", json=payload1, headers=auth_header(user1))
        response2 = client.post("/api/users/", json=payload2, headers=auth_header(user2))
        response3 = client.post("/api/users/", json=payload3, headers=auth_header(user3))
        response4 = client.post("/api/users/", json=payload4, headers=auth_header(user4))

    print(json.dumps(response1.get_json(), indent=2))
    print(json.dumps(response2.get_json(), indent=2))
    print(json.dumps(response3.get_json(), indent=2))
    print(json.dumps(response4.get_json(), indent=2))
    
    assert response1.status_code == 403
    assert response2.status_code == 403
    assert response3.status_code == 403
    assert response4.status_code == 403

def test_create_user_duplicate_email(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        cand_role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)
        create_user("U1", "u1@test.com", "pass", cand_role)

        payload = {"name": "X", "email": "u1@test.com", "role_id": cand_role.id}

        response = client.post("/api/users/", json=payload, headers=auth_header(admin))

    assert response.status_code == 400
    assert "Email already exists" in response.get_json()["error"]


# =========================================================
# GET USER BY ID
# =========================================================

def test_get_user_success(client, app):
    with app.app_context():
        role = create_role()
        user = create_user("T", "t@test.com", "pass", role)

        response = client.get(f"/api/users/{user.id}", headers=auth_header(user))

    assert response.status_code == 200
    assert response.get_json()["email"] == "t@test.com"


# =========================================================
# UPDATE USER
# =========================================================

def test_update_user_admin_success(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        cand_role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)
        user = create_user("U", "u@test.com", "pass", cand_role)

        payload = {"name": "Updated Name"}

        response = client.put(
            f"/api/users/{user.id}", json=payload, headers=auth_header(admin)
        )

    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 200
    assert response.get_json()["user"]["name"] == "Updated Name"


def test_update_user_non_admin_forbidden(client, app):
    with app.app_context():
        role = create_role("candidate")
        u1 = create_user("A", "a@test.com", "pass", role)
        u2 = create_user("B", "b@test.com", "pass", role)

        response = client.put(
            f"/api/users/{u2.id}", json={"name": "X"}, headers=auth_header(u1)
        )

    assert response.status_code == 403


def test_update_user_duplicate_email(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)
        u1 = create_user("U1", "u1@test.com", "pass", role)
        u2 = create_user("U2", "u2@test.com", "pass", role)

        payload = {"email": "u1@test.com"}

        response = client.put(
            f"/api/users/{u2.id}", json=payload, headers=auth_header(admin)
        )

    assert response.status_code == 400
    assert "Email already exists" in response.get_json()["error"]


# =========================================================
# DELETE USER
# =========================================================

def test_delete_user_admin_success(client, app):
    with app.app_context():
        admin_role = create_role("admin")
        cand_role = create_role("candidate")

        admin = create_user("Admin", "admin@test.com", "pass", admin_role)
        user = create_user("U", "u@test.com", "pass", cand_role)

        response = client.delete(
            f"/api/users/{user.id}", headers=auth_header(admin)
        )

    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 200
    assert "deleted" in response.get_json()["message"]


def test_delete_user_non_admin_forbidden(client, app):
    with app.app_context():
        role = create_role("candidate")
        u1 = create_user("A", "a@test.com", "pass", role)
        u2 = create_user("B", "b@test.com", "pass", role)

        response = client.delete(f"/api/users/{u2.id}", headers=auth_header(u1))

    assert response.status_code == 403


# =========================================================
# CHANGE PASSWORD
# =========================================================

def test_change_password_success(client, app):
    with app.app_context():
        role = create_role()
        user = create_user("U", "u@test.com", "pass", role)

        payload = {"old_password": "pass", "new_password": "newpass"}

        response = client.post(
            f"/api/users/{user.id}/change-password",
            json=payload,
            headers=auth_header(user)
        )

    assert response.status_code == 200
    assert "Password changed" in response.get_json()["message"]


def test_change_password_wrong_old_password(client, app):
    with app.app_context():
        role = create_role()
        user = create_user("U", "u@test.com", "pass", role)

        payload = {"old_password": "wrong", "new_password": "x"}

        response = client.post(
            f"/api/users/{user.id}/change-password",
            json=payload,
            headers=auth_header(user)
        )

    assert response.status_code == 400
    assert "incorrect" in response.get_json()["error"]
