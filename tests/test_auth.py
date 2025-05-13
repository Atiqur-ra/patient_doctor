
def test_login_success(client):

    register_response = client.post("/register/", json={
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "test123",
        "role": "patient"
    })
    assert register_response.status_code == 200

    login_response = client.post("/login", data={
        "username": "loginuser@example.com",
        "password": "test123"
    })

    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/register/", json={
        "name": "Wrong Password User",
        "email": "wrongpass@example.com",
        "password": "correctpassword",
        "role": "patient"
    })

    # Attempt login with wrong password
    response = client.post("/login", data={
        "username": "wrongpass@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_user_not_found(client):
    response = client.post("/login", data={
        "username": "nonexistent@example.com",
        "password": "irrelevant"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"
