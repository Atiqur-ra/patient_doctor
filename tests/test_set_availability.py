def get_token_for_doctor(client):
    register_payload = {
        "name": "Dr. Who",
        "email": "drwho@example.com",
        "password": "secret123",
        "role": "doctor",
        "department": "General"
    }
    client.post("/register", json=register_payload)

    login_payload = {
        "username": "drwho@example.com",
        "password": "secret123"
    }
    response = client.post("/login", data=login_payload)
    return response.json()["access_token"]


def test_set_availability_success(client):
    token = get_token_for_doctor(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "date": "2025-05-15",
        "start_time": "09:14:53.903Z",
        "end_time": "13:14:53.903Z"
    }

    response = client.post("/availability/set_availability", data=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["date"] == payload["date"]
    assert data["doctor_id"] is not None
    


def test_set_availability_unauthorized(client):
    payload = {
        "date": "2025-05-15",
        "start_time": "09:14:53.903Z",
        "end_time": "13:14:53.903Z"
    }

    response = client.post("/availability/set_availability", data=payload)

    assert response.status_code == 401
