def get_token(client):
    acces_token={}
    payload_patient={
        'name':"John Doe",
        'email':"johndoe@gmail.com",
        'password':"securepassword",
        'role':"patient"
    }
    response = client.post("/register",json=payload_patient)

    payload_doctor={
        'name':"Dr. Smith",
        'email':"smith@gmail.com",
        'password':"securepassword",
        'role':"doctor",
        'department':"ENT"
    }
    response = client.post("/register",json=payload_doctor)



    login_payload_patient={
        'username':"johndoe@gmail.com",
        'password':"securepassword"
    }
    response = client.post("/login",data=login_payload_patient)
    acces_token['patient_token']=response.json()["access_token"]

    login_payload_doctor={
        'username':"smith@gmail.com",
        'password':"securepassword",
    }
    response1 = client.post("/login",data=login_payload_doctor)
    acces_token['doctor_token']=response1.json()["access_token"]
    return acces_token


def test_book_appointment_success(client):

    token = get_token(client)
    doctor_headers = {'Authorization': f'Bearer {token["doctor_token"]}'}
    patient_headers = {'Authorization': f'Bearer {token["patient_token"]}'}

   
    payload = {
        "date": "2025-05-15",
        "start_time": "09:14:53.903Z",
        "end_time": "13:14:53.903Z"
    }
    response = client.post("/availability/set_availability",data=payload,headers=doctor_headers)
    assert response.status_code == 200

    booking_payload={
        'doctor_id':2,
        'slot_id':1
    }
    response1 = client.post("/appointments/book",data=booking_payload,headers=patient_headers)
    assert response1.status_code == 200