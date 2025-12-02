import json
import pytest
from app import db
from models import Vacancy

# ----------------------------
# Helper to create a Vacancy
# ----------------------------
def create_vacancy(**kwargs):
    v = Vacancy(
        title=kwargs.get("title", "Teacher"),
        description=kwargs.get("description", ""),
        requirements=kwargs.get("requirements", ""),
        location=kwargs.get("location", "NY"),
        school=kwargs.get("school", "ABC School"),
        level=kwargs.get("level", "Primary"),
        department=kwargs.get("department", "Math"),
        salary_range=kwargs.get("salary_range", "5 LPA"),
        employment_type=kwargs.get("employment_type", "full-time"),
        posted_by_id=kwargs.get("posted_by_id", "user-1"),
        status=kwargs.get("status", "active"),
    )
    db.session.add(v)
    db.session.commit()
    return v


# =====================================================================
# TEST: Create Vacancy
# =====================================================================
def test_create_vacancy_success(client, app):
    with app.app_context():
        payload = {
            "title": "Physics Teacher",
            "posted_by_id": "user-123",
            "location": "Delhi"
        }

        resp = client.post("/api/vacancies/", json=payload)
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 201
        assert body["vacancy"]["title"] == "Physics Teacher"
        assert body["vacancy"]["location"] == "Delhi"


def test_create_vacancy_missing_title(client, app):
    with app.app_context():
        payload = {
            "posted_by_id": "user-123",
        }

        resp = client.post("/api/vacancies/", json=payload)
        print(json.dumps(resp.get_json(), indent=2))

        assert resp.status_code == 400
        assert resp.get_json()["error"] == "Title is required"


def test_create_vacancy_missing_posted_by(client, app):
    with app.app_context():
        payload = {
            "title": "Teacher"
        }

        resp = client.post("/api/vacancies/", json=payload)
        print(json.dumps(resp.get_json(), indent=2))
        
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "Posted by ID is required"


# =====================================================================
# TEST: Get all vacancies (with filters)
# =====================================================================
def test_get_vacancies_with_filter(client, app):
    with app.app_context():
        create_vacancy(title="Bio Teacher", location="NY")
        create_vacancy(title="Chem Teacher", location="Boston")

        resp = client.get("/api/vacancies/?location=NY")
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 200
        assert len(body) == 1
        assert body[0]["location"] == "NY"


# =====================================================================
# TEST: Get single vacancy
# =====================================================================
def test_get_single_vacancy(client, app):
    with app.app_context():
        v = create_vacancy(title="English Teacher")

        resp = client.get(f"/api/vacancies/{v.id}")
        body = resp.get_json()
        print(json.dumps(body, indent=2))
        
        assert resp.status_code == 200
        assert body["title"] == "English Teacher"


# =====================================================================
# TEST: Update vacancy
# =====================================================================
def test_update_vacancy_success(client, app):
    with app.app_context():
        v = create_vacancy(title="Old Title")

        resp = client.put(
            f"/api/vacancies/{v.id}",
            json={"title": "New Title", "location": "Mumbai"}
        )
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 200
        assert body["vacancy"]["title"] == "New Title"
        assert body["vacancy"]["location"] == "Mumbai"


# =====================================================================
# TEST: Delete vacancy
# =====================================================================
def test_delete_vacancy_success(client, app):
    with app.app_context():
        v = create_vacancy()

        resp = client.delete(f"/api/vacancies/{v.id}")
        print(json.dumps(resp.get_json(), indent=2))

        assert resp.status_code == 200
        assert resp.get_json()["message"] == "Vacancy deleted successfully"

        # ensure removed
        assert Vacancy.query.get(v.id) is None


# =====================================================================
# TEST: Unique Locations
# =====================================================================
def test_get_locations(client, app):
    with app.app_context():
        create_vacancy(location="Delhi")
        create_vacancy(location="Mumbai")
        create_vacancy(location="Delhi")  # duplicate

        resp = client.get("/api/vacancies/locations")
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 200
        assert set(body["locations"]) == {"Delhi", "Mumbai"}
        assert body["count"] == 2


# =====================================================================
# TEST: Unique Schools
# =====================================================================
def test_get_schools(client, app):
    with app.app_context():
        create_vacancy(school="ABC School")
        create_vacancy(school="XYZ School")
        create_vacancy(school="ABC School")  # duplicate

        resp = client.get("/api/vacancies/schools")
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 200
        assert set(body["schools"]) == {"ABC School", "XYZ School"}
        assert body["count"] == 2


# =====================================================================
# TEST: Unique Levels
# =====================================================================
def test_get_levels(client, app):
    with app.app_context():
        create_vacancy(level="Primary")
        create_vacancy(level="Secondary")
        create_vacancy(level="Primary")

        resp = client.get("/api/vacancies/levels")
        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 200
        assert set(body["levels"]) == {"Primary", "Secondary"}
        assert body["count"] == 2
