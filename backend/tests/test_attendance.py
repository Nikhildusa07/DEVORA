from datetime import date

from fastapi.testclient import TestClient

from app.api.attendance import router
from main import app

client = TestClient(app)


def test_record_attendance():
    payload = {
        "student_id": "TEST_AUTO_001",
        "student_name": "Test Student",
        "date": str(date.today()),
        "status": "Present"
    }

    response = client.post(
        "/attendance/",
        json=payload
    )

    assert response.status_code == 201
    assert response.json()["student_id"] == "TEST_AUTO_001"


def test_duplicate_attendance():
    payload = {
        "student_id": "TEST_AUTO_002",
        "student_name": "Duplicate Test",
        "date": str(date.today()),
        "status": "Present"
    }

    first_response = client.post(
        "/attendance/",
        json=payload
    )

    second_response = client.post(
        "/attendance/",
        json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_get_attendance():
    response = client.get("/attendance/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
