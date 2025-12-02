import json
import io
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import FileStorage
from io import BytesIO

from models import (
    User, Role, OnBoardingDocument,
    OnboardingForm, OfferLetter
)

# ----------------------------------------------------
# Helper: create user + role
# ----------------------------------------------------

def create_user(role_name="employee"):
    role = Role(name=role_name)
    user = User(
        name="Test User",
        email=f"user_{role_name}@example.com",
        password="pass",
        role=role
    )
    return user

def auth_headers(user):
    token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {token}"}

# ----------------------------------------------------
# TEST 1: UPLOAD DOCUMENT
# ----------------------------------------------------

@patch("routes.onboarding_routes.save_onboarding_file")
@patch("routes.onboarding_routes.allowed_file", return_value=True)
def test_upload_document_success(mock_allowed, mock_save, client, app):
    with app.app_context():
        user = create_user("employee")
        db = app.extensions["sqlalchemy"].db
        db.session.add(user.role)
        db.session.add(user)
        db.session.commit()

        mock_save.return_value = (
            "/fake/path/document.pdf",
            "document.pdf",
            "application/pdf"
        )

        # proper file
        file_data = FileStorage(
            stream=BytesIO(b"fake file"),
            filename="document.pdf",
            content_type="application/pdf"
        )

        resp = client.post(
            "/api/onboarding/documents/upload",
            data={
                "file": file_data,
                "employee_id": str(user.id),
                "doc_type": "ID Proof",
            },
            headers=auth_headers(user),
            content_type="multipart/form-data"
        )

        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 201
        assert "document" in body


# ----------------------------------------------------
# TEST 2: GET DOCUMENTS (Authorized HR)
# ----------------------------------------------------

def test_get_documents_authorized(client, app):
    with app.app_context():
        db = app.extensions["sqlalchemy"].db

        hr = create_user("hr")
        employee = create_user("employee")

        db.session.add(hr.role)
        db.session.add(hr)
        db.session.add(employee.role)
        db.session.add(employee)
        db.session.commit()

        # Insert a document
        doc = OnBoardingDocument(
            employee_id=str(employee.id),
            doc_type="ID",
            filename="doc.pdf",
            file_path="/fake/path/doc.pdf",
            uploaded_by=str(hr.id),
        )
        db.session.add(doc)
        db.session.commit()

        resp = client.get(
            f"/api/onboarding/documents/{employee.id}",
            headers=auth_headers(hr),
        )

        docs = resp.get_json()
        print(json.dumps(docs, indent=2))
        
        assert resp.status_code == 200
        assert len(docs) == 1
        assert docs[0]["filename"] == "doc.pdf"

# ----------------------------------------------------
# TEST 3: VERIFY DOCUMENT
# ----------------------------------------------------

def test_verify_document_success(client, app):
    with app.app_context():
        db = app.extensions["sqlalchemy"].db

        hr = create_user("hr")
        user = create_user("employee")

        db.session.add(hr.role)
        db.session.add(hr)
        db.session.add(user.role)
        db.session.add(user)
        db.session.commit()

        doc = OnBoardingDocument(
            employee_id=str(user.id),
            doc_type="ID",
            filename="doc.pdf",
            file_path="/fake/doc.pdf",
            uploaded_by=str(hr.id),
            verified=False
        )
        db.session.add(doc)
        db.session.commit()

        resp = client.put(
            f"/api/onboarding/documents/{doc.id}/verify",
            json={"verifier_id": hr.id, "verified": True},
            headers=auth_headers(hr),
        )

        assert resp.status_code == 200
        b = resp.get_json()
        assert b["document"]["verified"] is True

# ----------------------------------------------------
# TEST 4: ONBOARDING PROGRESS
# ----------------------------------------------------

def test_onboarding_progress_basic(client, app):
    with app.app_context():
        db = app.extensions["sqlalchemy"].db
        from config import Config

        hr = create_user("hr")
        emp = create_user("employee")

        db.session.add(hr.role)
        db.session.add(hr)
        db.session.add(emp.role)
        db.session.add(emp)
        db.session.commit()

        # Insert ONE required document
        rd = Config.ONBOARDING_REQUIRED_DOCS[0]
        doc = OnBoardingDocument(
            employee_id=str(emp.id),
            doc_type=rd,
            filename="rd.pdf",
            file_path="/fake/rd.pdf",
            uploaded_by=str(hr.id),
            verified=True
        )
        db.session.add(doc)
        db.session.commit()

        resp = client.get(
            f"/api/onboarding/progress/{emp.id}",
            headers=auth_headers(hr),
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert "progess_percent" in data
        assert data["employee_id"] == str(emp.id)

# ----------------------------------------------------
# TEST 5: GENERATE OFFER LETTER
# ----------------------------------------------------


@patch("os.makedirs")
@patch("docx.document.Document.save", return_value=None)
@patch("routes.onboarding_routes.get_data_root", return_value="/fake")
def test_generate_offer_letter_success(mock_root, mock_save, mock_makedirs, client, app):
    with app.app_context():

        db = app.extensions["sqlalchemy"].db

        # create HR user (allowed role)
        hr_user = create_user("hr")
        db.session.add(hr_user.role)
        db.session.add(hr_user)
        db.session.commit()

        payload = {
            "employee_id": str(hr_user.id),
            "template_vars": {
                "employee_id": str(hr_user.id),
                "candidate_name": "John Doe",
                "job_title": "Teacher",
                "salary": "5 LPA"
            }
        }

        resp = client.post(
            "/api/onboarding/offer-letter/generate",
            json=payload,
            headers=auth_headers(hr_user)
        )

        body = resp.get_json()
        print(json.dumps(body, indent=2))

        assert resp.status_code == 201
        assert "offer" in body
        assert "document" in body

# ----------------------------------------------------
# TEST 6: SUBMIT FORM (JSON MODE)
# ----------------------------------------------------

def test_submit_form_json_success(client, app):
    with app.app_context():
        db = app.extensions["sqlalchemy"].db
        from config import Config

        # ensure schema exists
        form_type = list(Config.ONBOARDING_FORM_SCHEMAS.keys())[0]
        required_fields = [
            f["name"]
            for f in Config.ONBOARDING_FORM_SCHEMAS[form_type]["fields"]
            if f.get("required")
        ]

        hr = create_user("hr")
        emp = create_user("employee")
        db.session.add(hr.role)
        db.session.add(hr)
        db.session.add(emp.role)
        db.session.add(emp)
        db.session.commit()

        form_data = {field: "value" for field in required_fields}

        resp = client.post(
            "/api/onboarding/forms/submit",
            json={
                "employee_id": str(emp.id),
                "form_type": form_type,
                "form_data": form_data,
            },
            headers=auth_headers(hr),
        )

        data = resp.get_json()
        print(json.dumps(data, indent=2))
        
        assert resp.status_code == 201
        assert "submission" in data
        assert data["submission"]["form_type"] == form_type
