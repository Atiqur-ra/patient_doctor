from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "role": "doctor",
        "department": "Cardiology"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"
