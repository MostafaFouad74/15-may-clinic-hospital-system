from datetime import datetime, timedelta

def test_admin_create_doctor(client, admin_token):
    response = client.post(
        "/admin/create-doctor",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "doctor1",
            "password": "docpassword",
            "full_name": "Dr. Smith",
            "specialty": "Cardiology",
            "department": "Cardiology",
            "work_start_hour": 9,
            "work_end_hour": 17
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor created successfully"


def test_patient_booking_and_double_booking(client, admin_token):
    # 1. Admin creates doctor
    client.post(
        "/admin/create-doctor",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "doctor2",
            "password": "docpassword",
            "full_name": "Dr. Jones",
            "specialty": "Neurology",
            "department": "Neurology",
            "work_start_hour": 9,
            "work_end_hour": 17
        }
    )

    # Get doctor ID
    docs_response = client.get("/doctor/all")
    doc_id = [d["id"] for d in docs_response.json() if d["full_name"] == "Dr. Jones"][0]

    # 2. Register Patient
    client.post(
        "/register",
        json={
            "username": "patient3",
            "password": "password123",
            "first_name": "Alice",
            "last_name": "Wonder",
            "age": 28,
            "phone": "01212345678",
            "address": "Alex",
            "gender": "female",
            "department": "Neurology"
        }
    )
    
    # Login Patient
    login_resp = client.post(
        "/login",
        data={"username": "patient3", "password": "password123"}
    )
    patient_token = login_resp.json()["access_token"]

    # 3. Book Appointment
    # Setup tomorrow at 10:00 AM
    tomorrow = datetime.now() + timedelta(days=1)
    appt_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

    book_resp = client.post(
        "/patient/appointments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={
            "doctor_id": doc_id,
            "appointment_date": appt_time.isoformat()
        }
    )
    assert book_resp.status_code == 200
    assert book_resp.json()["message"] == "Appointment booked successfully"

    # 4. Test Double Booking
    book_resp_2 = client.post(
        "/patient/appointments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={
            "doctor_id": doc_id,
            "appointment_date": appt_time.isoformat()
        }
    )
    assert book_resp_2.status_code == 400
    assert "already booked" in book_resp_2.json()["detail"].lower()


def test_appointment_status_transition(client, admin_token):
    # Book an appointment
    # We will reuse the admin token to log in as doctor to change status
    
    # Register Doctor
    client.post(
        "/admin/create-doctor",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "doctor3",
            "password": "docpassword",
            "full_name": "Dr. House",
            "specialty": "Diagnostics",
            "department": "General",
            "work_start_hour": 9,
            "work_end_hour": 17
        }
    )
    docs_response = client.get("/doctor/all")
    doc_id = [d["id"] for d in docs_response.json() if d["full_name"] == "Dr. House"][0]

    # Register Patient
    client.post(
        "/register",
        json={
            "username": "patient4",
            "password": "password123",
            "first_name": "Bob",
            "last_name": "Builder",
            "age": 35,
            "phone": "01512345678",
            "address": "Cairo",
            "gender": "male",
            "department": "General"
        }
    )
    login_resp = client.post("/login", data={"username": "patient4", "password": "password123"})
    patient_token = login_resp.json()["access_token"]

    tomorrow = datetime.now() + timedelta(days=1)
    appt_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)
    
    book_resp = client.post(
        "/patient/appointments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"doctor_id": doc_id, "appointment_date": appt_time.isoformat()}
    )
    appt_id = book_resp.json()["appointment_id"]

    # Login as Doctor
    doc_login_resp = client.post("/login", data={"username": "doctor3", "password": "docpassword"})
    doc_token = doc_login_resp.json()["access_token"]

    # Update to Completed
    update_resp = client.put(
        f"/doctor/appointments/{appt_id}/status",
        headers={"Authorization": f"Bearer {doc_token}"},
        json={"status": "Completed"}
    )
    assert update_resp.status_code == 200

    # Try updating again -> Should fail
    update_resp_2 = client.put(
        f"/doctor/appointments/{appt_id}/status",
        headers={"Authorization": f"Bearer {doc_token}"},
        json={"status": "Cancelled"}
    )
    assert update_resp_2.status_code == 400
    assert "Cannot change status" in update_resp_2.json()["detail"]
