def get_token_for_doctor(client):
    register_payload = {
        "name": "Dr. Who",
        "email": "drwho@example.com",
        "password": "secret123",
        "role": "patient",
        "department": None
    }
    client.post("/register", json=register_payload)

    login_payload = {
        "username": "drwho@example.com",
        "password": "secret123"
    }
    response = client.post("/login", data=login_payload)
    return response.json()["access_token"]

def test_search_availability_sucess_without_params(client):
    token = get_token_for_doctor(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload={
        "name":None,
        "department":None
    }
    response = client.get("/search/search-doctors", params=payload,headers=headers)
    assert response.status_code == 200

def test_search_availability_sucess_with_params(client):
    token = get_token_for_doctor(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload={
        "name":None,
        "department":"ENT"
    }
    response = client.get("/search/search-doctors", params=payload,headers=headers)
    assert response.status_code == 200