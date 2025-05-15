
def test_register_patient(client):
    payload = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password": "securepassword",
        "role": "patient"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["email"] == "johndoe@example.com"
    assert data["name"] == "John Doe"
    assert data["role"] == "patient"

def test_register_success(client):
    response = client.post("/register", json={
        "name": "John Doe1",
        "email": "janedoe@example.com",
        "password": "securepassword1",
        "role": "patient",
       
    })
    assert response.status_code == 200
    assert response.json()["email"] == "janedoe@example.com"

def test_register_duplicate_email(client):
    # First registration
    client.post("/register", json={
        "name": "Jane Doe",
        "email": "janedoe@example.com",
        "password": "securepassword",
        "role": "patient"
    })

    # Try registering again with same email
    response = client.post("/register", json={
        "name": "Jane Doe 2",
        "email": "janedoe@example.com",
        "password": "securepassword",
        "role": "patient"
    })

    assert response.status_code == 400

def test_register_doctor_without_department(client):
    response = client.post("/register", json={
        "name": "Dr. Smith",
        "email": "drsmith@example.com",
        "password": "securepassword",
        "role": "doctor",
        "department": None
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Doctor must have a department"