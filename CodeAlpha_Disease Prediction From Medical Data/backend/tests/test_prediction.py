import os

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _login():
    email = os.getenv("HEARTTRACK_DEMO_EMAIL", "demo@hearttrack.ai")
    password = os.getenv("HEARTTRACK_DEMO_PASSWORD", "HeartTrack@2026")
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200


def test_prediction_contract_when_model_ready():
    _login()
    health = client.get("/api/health").json()
    if not health["model_ready"]:
        return
    payload = {
        "age": 54,
        "sex": 1,
        "cp": 3,
        "trestbps": 130,
        "chol": 246,
        "fbs": 0,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 1.0,
        "slope": 2,
        "ca": 0,
        "thal": 3,
    }
    response = client.post("/api/prediction/heart", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["probability"] <= 1
    assert body["risk_level"] in {"Low", "Moderate", "High", "Very High"}
    assert len(body["influences"]) <= 6
