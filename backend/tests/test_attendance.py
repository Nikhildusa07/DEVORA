from datetime import date

from fastapi.testclient import TestClient

from main import app
from app.database import Base, engine, SessionLocal
from app.models.attendance import AttendanceModel


client = TestClient(app)


def clean_test_records():
    db = SessionLocal()

    try:
        db.query(AttendanceModel).filter(
            AttendanceModel.student_id.in_(
                [
                    "TEST_AUTO_001",
                    "TEST_AUTO_002"
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.commit()

    finally:
        db.close()


def setup_module():
    Base.metadata.create_all(bind=engine)
    clean_test_records()


def teardown_module():
    clean_test_records()


def test_record_attendance():

    clean_test_records()

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

    data = response.json()

    assert data["student_id"] == "TEST_AUTO_001"
    assert data["student_name"] == "Test Student"
    assert data["status"] == "Present"


def test_duplicate_attendance():

    clean_test_records()

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

    response = client.get(
        "/attendance/"
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list
    )