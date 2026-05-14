def test_unauthorized_access(client):
    # Missing token -> 401
    response = client.get("/admin/appointments")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_role_based_access(client, admin_token):
    # 1. Register a Patient
    client.post(
        "/register",
        json={
            "username": "patient_rbac",
            "password": "password123",
            "first_name": "Test",
            "last_name": "Patient",
            "age": 20,
            "phone": "01099999999",
            "address": "Cairo",
            "gender": "male",
            "department": "General"
        }
    )
    
    # 2. Login as Patient
    login_resp = client.post("/login", data={"username": "patient_rbac", "password": "password123"})
    patient_token = login_resp.json()["access_token"]

    # 3. Try to access Admin route as Patient -> 403
    admin_route_resp = client.get(
        "/admin/appointments",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert admin_route_resp.status_code == 403
    assert "Admins only" in admin_route_resp.json()["detail"]
    
    # 4. Try to access Doctor route as Patient -> 403
    doctor_route_resp = client.get(
        "/doctor/appointments/me",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert doctor_route_resp.status_code == 403
    assert "Doctors only" in doctor_route_resp.json()["detail"]


def test_edge_cases_and_validation(client, admin_token):
    # 1. Invalid ID -> 404
    resp_404 = client.get(
        "/admin/patients/9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Patient not found"

    # 2. Invalid inputs -> 422
    # Invalid email and missing required field
    resp_422 = client.post(
        "/admin/create-doctor",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "doc_invalid",
            # password missing
            "full_name": "Dr. Invalid",
            "specialty": "General",
            "email": "not-an-email"
        }
    )
    assert resp_422.status_code == 422

    # 3. Duplicate User -> 400
    # The admin user already exists as "admin_test" in conftest.py
    # Try creating doctor with same username
    resp_duplicate = client.post(
        "/admin/create-doctor",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "admin_test", # Existing username
            "password": "newpassword",
            "full_name": "Duplicate Doc",
            "specialty": "General",
            "department": "General",
            "work_start_hour": 9,
            "work_end_hour": 17
        }
    )
    assert resp_duplicate.status_code == 400
    assert "Username already exists" in resp_duplicate.json()["detail"]


def test_unauthorized_data_access(client, admin_token):
    # 1. Register Patient A
    client.post("/register", json={
        "username": "patient_a", "password": "pwd", "first_name": "A", "last_name": "A",
        "age": 20, "phone": "01000000000", "address": "X", "gender": "male", "department": "General"
    })
    token_a = client.post("/login", data={"username": "patient_a", "password": "pwd"}).json()["access_token"]

    # 2. Register Patient B
    client.post("/register", json={
        "username": "patient_b", "password": "pwd", "first_name": "B", "last_name": "B",
        "age": 20, "phone": "01100000000", "address": "Y", "gender": "male", "department": "General"
    })
    token_b = client.post("/login", data={"username": "patient_b", "password": "pwd"}).json()["access_token"]

    # 3. Create Doctor
    client.post("/admin/create-doctor", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "username": "doc_access", "password": "pwd", "full_name": "Dr. Access", "specialty": "Gen",
        "department": "General", "work_start_hour": 8, "work_end_hour": 16
    })
    doc_id = [d["id"] for d in client.get("/doctor/all").json() if d["full_name"] == "Dr. Access"][0]

    # 4. Patient A books appointment
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    appt_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    book_resp = client.post("/patient/appointments", headers={"Authorization": f"Bearer {token_a}"}, json={
        "doctor_id": doc_id, "appointment_date": appt_time.isoformat()
    })
    appt_id = book_resp.json()["appointment_id"]

    # 5. Patient B tries to cancel Patient A's appointment -> 403 Forbidden
    cancel_resp = client.delete(f"/patient/appointments/{appt_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert cancel_resp.status_code == 403
    assert "own appointments" in cancel_resp.json()["detail"].lower()
