from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app, get_db

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
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/incidents")
        assert response.status_code == 200
        assert "incidents" in response.json()
    finally:
        app.dependency_overrides.pop(get_db, None)
