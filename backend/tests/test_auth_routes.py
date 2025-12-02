# tests/test_auth_routes.py
import json
import pytest
from app import db
from models import User, Role
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------
# HELPER: create a role
# ---------------------------------------------------------
def create_role(name="Employee", description="Regular employee"):
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return role.id


# ---------------------------------------------------------
# HELPER: create a user directly in DB (for login tests)
# ---------------------------------------------------------
def create_user(name, email, password, role_id, status="active"):
    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role_id=role_id,
        status=status
    )
    db.session.add(user)
    db.session.commit()
    return user


# =========================================================
#                   REGISTER TEST CASES
# =========================================================

def test_register_user_success(client, app):
    with app.app_context():
        role_id = create_role()

    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123",
            "role_id": role_id,
        },
    )

    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 201
    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "test@example.com"


def test_register_user_already_exists(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("John", "john@example.com", "pass123", role_id)

    response = client.post(
        "/api/auth/register",
        json={
            "name": "Another User",
            "email": "john@example.com",
            "password": "testpass",
            "role_id": role_id,
        },
    )

    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 400
    assert response.get_json()["error"] == "User already exists"


def test_register_missing_fields(client):
    
    response = client.post(
        "/api/auth/register",
        json={"email": "bad@example.com"}
    )
    
    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 500


# =========================================================
#                        LOGIN TESTS
# =========================================================

def test_login_success(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("LoginUser", "login@example.com", "validpass", role_id)

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "validpass"},
    )

    data = response.get_json()
    print(json.dumps(data, indent=2))
    assert response.status_code == 200
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "login@example.com"


def test_login_user_not_found(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "something"},
    )
    
    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


def test_login_invalid_password(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("UserX", "x@example.com", "correctpass", role_id)

    response = client.post(
        "/api/auth/login",
        json={"email": "x@example.com", "password": "wrongpass"},
    )

    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"


def test_login_user_inactive(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("InactiveGuy", "inactive@example.com", "aa123", role_id, status="inactive")

    response = client.post(
        "/api/auth/login",
        json={"email": "inactive@example.com", "password": "aa123"}
    )
    
    print(json.dumps(response.get_json(), indent=2))

    assert response.status_code == 403
    assert response.get_json()["error"] == "User account is not active"


# =========================================================
#                       LOGOUT TEST
# =========================================================

def test_logout_success(client, app):
    with app.app_context():
        role_id = create_role()
        user = create_user("L", "logout@example.com", "pass123", role_id)

    login = client.post(
        "/api/auth/login",
        json={"email": "logout@example.com", "password": "pass123"},
    )
    token = login.get_json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Logout successful"


def test_logout_without_token(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 401


# =========================================================
#                  REFRESH TOKEN TESTS
# =========================================================

def test_refresh_token_success(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("R", "refresh@example.com", "pass123", role_id)

    login = client.post(
        "/api/auth/login",
        json={"email": "refresh@example.com", "password": "pass123"},
    )
    refresh_token = login.get_json()["refresh_token"]

    response = client.post(
        "/api/auth/refresh-token",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_refresh_token_using_access_token_should_fail(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("R2", "refresh2@example.com", "pass123", role_id)

    login = client.post(
        "/api/auth/login",
        json={"email": "refresh2@example.com", "password": "pass123"},
    )
    access_token = login.get_json()["access_token"]

    response = client.post(
        "/api/auth/refresh-token",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422  # Flask-JWT-Extended rule


# =========================================================
#                           /me TESTS
# =========================================================

def test_me_success(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("MeUser", "me@example.com", "pass123", role_id)

    login = client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "password": "pass123"},
    )
    token = login.get_json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["email"] == "me@example.com"


def test_me_user_not_found(client, app):
    with app.app_context():
        role_id = create_role()
        create_user("Temp", "temp@example.com", "xx", role_id)

    login = client.post(
        "/api/auth/login",
        json={"email": "temp@example.com", "password": "xx"},
    )
    token = login.get_json()["access_token"]

    # DELETE user manually
    with app.app_context():
        User.query.delete()
        db.session.commit()

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"


# =========================================================
#                   ROLES TESTS
# =========================================================

def test_get_roles(client, app):
    with app.app_context():
        create_role("Admin")
        create_role("Manager")

    response = client.get("/api/auth/roles")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_create_role_success(client):
    response = client.post(
        "/api/auth/roles",
        json={"name": "Support", "description": "Support role"},
    )

    assert response.status_code == 201
    assert response.get_json()["role"]["name"] == "Support"


def test_create_role_missing_name_should_fail(client):
    response = client.post(
        "/api/auth/roles",
        json={"description": "Missing name"},
    )

    assert response.status_code == 500
    assert "error" in response.get_json()
    
