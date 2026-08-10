from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_runtime_registration_login_and_logout():
    email = f"analyst-{uuid4().hex[:8]}@example.com"
    payload = {"full_name": "Test Analyst", "email": email, "password": "HeartTrack2026"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["user"]["email"] == email

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["display_name"] == "Test Analyst"

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204


def test_profile_can_update_display_name_and_email():
    original_email = f"profile-{uuid4().hex[:8]}@example.com"
    updated_email = f"updated-{uuid4().hex[:8]}@example.com"
    register = client.post(
        "/api/auth/register",
        json={"full_name": "Original Analyst", "email": original_email, "password": "HeartTrack2026"},
    )
    assert register.status_code == 201

    update = client.post(
        "/api/auth/profile",
        json={"display_name": "Saad Analyst", "email": updated_email},
    )
    assert update.status_code == 200
    assert update.json()["display_name"] == "Saad Analyst"
    assert update.json()["email"] == updated_email

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["display_name"] == "Saad Analyst"
    assert me.json()["email"] == updated_email

    client.post("/api/auth/logout")
