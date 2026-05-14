from datetime import datetime, timedelta


def test_admin_crud_doctors(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    create_resp = client.post(
        "/admin/create-doctor",
        headers=headers,
        json={
            "username": "crud_doctor",
            "password": "docpassword",
            "full_name": "Dr. CRUD",
            "specialty": "Oncology",
            "department": "Oncology",
            "work_start_hour": 8,
            "work_end_hour": 16,
        },
    )
    assert create_resp.status_code == 200
    doc_id = create_resp.json()["doctor_id"]

    get_resp = client.get(f"/admin/doctors/{doc_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["full_name"] == "Dr. CRUD"

    update_resp = client.put(
        f"/admin/doctors/{doc_id}",
        headers=headers,
        json={"specialty": "Pediatrics"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["specialty"] == "Pediatrics"

    delete_resp = client.delete(f"/admin/doctors/{doc_id}", headers=headers)
    assert delete_resp.status_code == 200

    get_deleted = client.get(f"/admin/doctors/{doc_id}", headers=headers)
    assert get_deleted.status_code == 404


def test_admin_crud_patients(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    register_resp = client.post(
        "/register",
        json={
            "username": "crud_patient",
            "password": "password123",
            "first_name": "CRUD",
            "last_name": "Patient",
            "age": 40,
            "phone": "01088888888",
            "address": "Alex",
            "gender": "male",
            "department": "General",
        },
    )
    assert register_resp.status_code in (200, 201)

    get_all = client.get("/admin/patients", headers=headers)
    assert get_all.status_code == 200

    patients = get_all.json()
    matching_patients = [p for p in patients if p["username"] == "crud_patient"]
    assert len(matching_patients) == 1

    patient_id = matching_patients[0]["id"]

    get_single = client.get(f"/admin/patients/{patient_id}", headers=headers)
    assert get_single.status_code == 200
    assert get_single.json()["first_name"] == "CRUD"

    update_resp = client.put(
        f"/admin/patients/{patient_id}",
        headers=headers,
        json={"age": 41, "address": "Cairo Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["age"] == 41
    assert update_resp.json()["address"] == "Cairo Updated"

    delete_resp = client.delete(f"/admin/patients/{patient_id}", headers=headers)
    assert delete_resp.status_code == 200

    get_deleted = client.get(f"/admin/patients/{patient_id}", headers=headers)
    assert get_deleted.status_code == 404


def test_error_handling(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp_404 = client.get("/admin/doctors/99999", headers=headers)
    assert resp_404.status_code == 404

    resp_422 = client.post(
        "/admin/create-doctor",
        headers=headers,
        json={"username": "doc"},
    )
    assert resp_422.status_code == 422

    resp_dup = client.post(
        "/admin/create-doctor",
        headers=headers,
        json={
            "username": "admin_test",
            "password": "pwd",
            "full_name": "Test",
            "specialty": "Gen",
            "department": "Gen",
            "work_start_hour": 9,
            "work_end_hour": 17,
        },
    )
    assert resp_dup.status_code == 400
    assert "already exists" in resp_dup.json()["detail"].lower()