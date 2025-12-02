import json
from models import Role
from app import db

# -----------------------------------------
# GET /roles/  (empty)
# -----------------------------------------
def test_get_roles_empty(client):
    resp = client.get('/api/roles/')
    assert resp.status_code == 200
    assert resp.get_json() == []


# -----------------------------------------
# GET /roles/ (with data)
# -----------------------------------------
def test_get_roles_with_data(client):
    r1 = Role(name="Admin", description="Full access")
    r2 = Role(name="User", description="Limited access")
    db.session.add_all([r1, r2])
    db.session.commit()

    resp = client.get('/api/roles/')
    data = resp.get_json()

    print(json.dumps(data, indent=2))
    assert resp.status_code == 200
    assert len(data) == 2
    assert any(role["name"] == "Admin" for role in data)
    assert any(role["name"] == "User" for role in data)


# -----------------------------------------
# POST /roles/  (success)
# -----------------------------------------
def test_create_role_success(client):
    payload = {
        "name": "Manager",
        "description": "Handles teams"
    }

    resp = client.post('/api/roles/', json=payload)
    data = resp.get_json()

    print(json.dumps(data, indent=2))
    assert resp.status_code == 201
    assert data["message"] == "Role created successfully"
    assert data["role"]["name"] == "Manager"

    # verify DB insert
    role = Role.query.filter_by(name="Manager").first()
    assert role is not None


# -----------------------------------------
# POST /roles/ (duplicate name)
# -----------------------------------------
def test_create_role_duplicate_name(client):
    r = Role(name="Dev", description="Developer")
    db.session.add(r)
    db.session.commit()

    payload = {
        "name": "Dev",
        "description": "Another dev"
    }

    resp = client.post('/api/roles/', json=payload)
    data = resp.get_json()

    print(json.dumps(data, indent=2))
    assert resp.status_code == 400
    assert data["error"] == "Role name already exists"


# -----------------------------------------
# GET /roles/<id> (success)
# -----------------------------------------
def test_get_role_success(client):
    r = Role(name="Tester", description="Tests stuff")
    db.session.add(r)
    db.session.commit()

    resp = client.get(f'/api/roles/{r.id}')
    data = resp.get_json()

    print(json.dumps(data, indent=2))
    assert resp.status_code == 200
    assert data["name"] == "Tester"


# -----------------------------------------
# GET /roles/<id> (not found)
# -----------------------------------------
def test_get_role_not_found(client):
    r_id = "999"
    resp = client.get(f'/api/roles/{r_id}')
    print(json.dumps(resp.get_json(), indent=2))
    assert resp.status_code == 404
