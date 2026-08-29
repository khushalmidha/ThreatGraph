from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_policies():
    response = client.get("/policies")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert "isolated_hosts" in data

def test_unauthorized_containment():
    # Attempt containment without token
    response = client.post("/containment/isolate/10.0.0.99")
    assert response.status_code == 403

def test_get_incidents():
    response = client.get("/incidents")
    assert response.status_code == 200
    assert "incidents" in response.json()
