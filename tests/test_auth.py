def test_register_patient(client):
    response = client.post(
        "/register",
        json={
            "username": "patient1",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "phone": "01012345678",
            "address": "Cairo",
            "gender": "male",
            "department": "General"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Patient registered successfully"


def test_login_success(client):
    # Register first
    client.post(
        "/register",
        json={
            "username": "patient2",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 25,
            "phone": "01112345678",
            "address": "Giza",
            "gender": "female",
            "department": "General"
        }
    )
    
    # Login
    response = client.post(
        "/login",
        data={"username": "patient2", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post(
        "/login",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
