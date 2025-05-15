def test_login_success(client):
    # First, register a user
    register_payload = {
        "name": "Login Test User",
        "email": "logintest@example.com",
        "password": "securepassword",
        "role": "patient"
    }
    client.post("/register", json=register_payload)

    # Attempt login
    login_payload = {
        "username": "logintest@example.com",
        "password": "securepassword"
    }

    response = client.post("/login", data=login_payload)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    # Try to login with an invalid user
    login_payload = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/login", data=login_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_wrong_password(client):

    register_payload = {
        "name": "Wrong Password User",
        "email": "wrongpass@example.com",
        "password": "correctpassword",
        "role": "patient"
    }
    client.post("/register", json=register_payload)

    # Try to login with wrong password
    login_payload = {
        "username": "wrongpass@example.com",
        "password": "incorrectpassword"
    }

    response = client.post("/login", data=login_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"
