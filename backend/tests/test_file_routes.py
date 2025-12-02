import os
import io
import json
import uuid
from models import User, Role, File
from flask_jwt_extended import create_access_token
from app import db


# JWT Headers helper --------------------------------------------------------
def auth_header(user):
    """Generate JWT header for a test user."""
    token = create_access_token(identity=user.id)
    return {"Authorization": f"Bearer {token}"}

# Utility helpers --------------------------------------------------------
def create_role(name):
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return role


def create_user(name, email, password, role):
    user = User(name=name, email=email, password=password, role_id=role.id)
    db.session.add(user)
    db.session.commit()
    return user


def create_fake_file(content=b"Hello world", ext="pdf"):
    """Creates a real temp file object for upload tests."""
    return io.BytesIO(content), f"test_{uuid.uuid4()}.{ext}"


# -----------------------------------------------------------------------
# 1. TEST FILE UPLOAD
# -----------------------------------------------------------------------

def test_upload_file_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        test_file, filename = create_fake_file()

        data = {
            "file": (test_file, filename),
            "category": "resume",
            "description": "Test file",
            "is_public": "true"
        }

        resp = client.post(
            "/api/files/upload",
            headers=auth_header(user),
            data=data,
            content_type="multipart/form-data"
        )

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["success"] is True
    assert "data" in body
    assert body["data"]["category"] == "resume"


def test_upload_file_invalid_extension(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        fake_file, filename = create_fake_file(ext="txt")

        data = {
            "file": (fake_file, filename)
        }

        resp = client.post(
            "/api/files/upload",
            headers=auth_header(user),
            data=data,
            content_type="multipart/form-data"
        )

    assert resp.status_code == 400
    assert "Invalid file type" in resp.get_json()["error"]


def test_upload_file_missing_file(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        resp = client.post(
            "/api/files/upload",
            headers=auth_header(user),
            data={},
            content_type="multipart/form-data"
        )

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "No file provided"


# -----------------------------------------------------------------------
# 2. DOWNLOAD FILE
# -----------------------------------------------------------------------

def test_download_file_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("Admin", "admin@test.com", "pass", role)

        fake_file, filename = create_fake_file()
        file_path = f"/tmp/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello PDF content")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=20,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user.id,
            category="doc",
            description="test",
            is_public=False
        )
        db.session.add(record)
        db.session.commit()

        resp = client.get(
            f"/api/files/{record.id}/download",
            headers=auth_header(user),
        )

    print("TEST DOWNLOAD FILE SUCCESS:", resp.get_data()[:50])

    # ✔ STATUS
    assert resp.status_code == 200

    # ✔ FILE BYTES RETURNED
    assert resp.data != b""
    assert b"Hello PDF content" in resp.data

    # ✔ HEADERS
    assert resp.is_json is False
    assert resp.headers["Content-Type"] == "application/pdf"

    cd = resp.headers.get("Content-Disposition")
    assert cd is not None
    assert "attachment" in cd
    assert record.original_filename in cd

def test_download_file_permission_denied(client, app):
    with app.app_context():
        role_user = create_role("candidate")
        user1 = create_user("U1", "u1@test.com", "pass", role_user)
        user2 = create_user("U2", "u2@test.com", "pass", role_user)

        # File owned by user1
        fake_file, filename = create_fake_file()
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=5,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user1.id,
            category="doc",
            description="test",
            is_public=False
        )
        db.session.add(record)
        db.session.commit()

        resp = client.get(
            f"/api/files/{record.id}/download",
            headers=auth_header(user2),
        )

    assert resp.status_code == 403
    assert "Access denied" in resp.get_json()["error"]


# -----------------------------------------------------------------------
# 3. DELETE FILE
# -----------------------------------------------------------------------

def test_delete_file_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("Admin", "admin@test.com", "pass", role)

        # Create a real file
        fake_file, filename = create_fake_file()
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=5,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user.id,
            category="doc",
            description="test",
            is_public=True
        )
        db.session.add(record)
        db.session.commit()

        resp = client.delete(
            f"/api/files/{record.id}",
            headers=auth_header(user)
        )

    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_delete_file_permission_denied(client, app):
    with app.app_context():
        role = create_role("candidate")
        user1 = create_user("A", "a@test.com", "pass", role)
        user2 = create_user("B", "b@test.com", "pass", role)

        fake_file, filename = create_fake_file()
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=5,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user1.id,
            category="doc",
            description="test",
            is_public=False
        )
        db.session.add(record)
        db.session.commit()

        resp = client.delete(
            f"/api/files/{record.id}",
            headers=auth_header(user2)
        )
        
        print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 403


# -----------------------------------------------------------------------
# 4. PREVIEW FILE
# -----------------------------------------------------------------------

def test_preview_pdf_metadata_only(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        fake_file, filename = create_fake_file(b"dummy pdf", "pdf")
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"dummy pdf")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=10,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user.id,
            category="doc",
            description="test",
            is_public=True
        )
        db.session.add(record)
        db.session.commit()

        resp = client.get(
            f"/api/files/{record.id}/preview",
            headers=auth_header(user)
        )

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert resp.get_json()["preview_type"] == "metadata"


# -----------------------------------------------------------------------
# 5. GET FILES LISTING
# -----------------------------------------------------------------------

def test_get_files_list(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        resp = client.get("/api/files/", headers=auth_header(user))

    assert resp.status_code == 200
    assert "data" in resp.get_json()


# -----------------------------------------------------------------------
# 6. FILE INFO
# -----------------------------------------------------------------------

def test_get_file_info_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("A", "a@test.com", "pass", role)

        fake_file, filename = create_fake_file()
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=5,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user.id,
            category="doc",
            description="test",
            is_public=True
        )
        db.session.add(record)
        db.session.commit()

        resp = client.get(
            f"/api/files/{record.id}",
            headers=auth_header(user)
        )

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert resp.get_json()["original_filename"] == filename


# -----------------------------------------------------------------------
# 7. UPDATE METADATA
# -----------------------------------------------------------------------

def test_update_metadata_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("Admin", "admin@test.com", "pass", role)

        fake_file, filename = create_fake_file()
        file_path = f"./uploads/files/{uuid.uuid4()}_{filename}"
        with open(file_path, "wb") as f:
            f.write(b"Hello")

        record = File(
            filename=os.path.basename(file_path),
            original_filename=filename,
            file_path=file_path,
            file_size=5,
            file_type="pdf",
            mime_type="application/pdf",
            uploaded_by_id=user.id,
            category="doc",
            description="old",
            is_public=False
        )
        db.session.add(record)
        db.session.commit()

        payload = {"category": "resume", "description": "Updated desc", "is_public": True}

        resp = client.put(
            f"/api/files/{record.id}",
            headers=auth_header(user),
            json=payload
        )

    print(json.dumps(resp.get_json(), indent=2))

    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


# -----------------------------------------------------------------------
# 8. FILE STATS
# -----------------------------------------------------------------------

def test_get_file_statistics_success(client, app):
    with app.app_context():
        role = create_role("admin")
        user = create_user("AdminUser", "admin@test.com", "pass", role)

        resp = client.get("/api/files/stats", headers=auth_header(user))

    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_files" in data
    assert "files_by_type" in data
