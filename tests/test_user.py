from fastapi.testclient import TestClient
from main import app

# client = TestClient(app)

# def test_register_user():
#     response = client.post("/register", json={
#         "name": "Test User",
#         "email": "testuser@example.com",
#         "password": "testpass123",
#         "role": "doctor",
#         "department": "Cardiology"
#     })
#     assert response.status_code == 200
#     assert response.json()["email"] == "testuser@example.com"

# tests/test_user.py

def test_register_user(client):
    response = client.post("/register/", json={
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password": "test123",
        "role": "patient"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "johndoe@example.com"
    assert data["role"] == "patient"

