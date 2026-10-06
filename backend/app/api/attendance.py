from datetime import date as DateType
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse
)
from app.services.attendance_service import AttendanceService


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED
)
def record_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    return AttendanceService.record_attendance(
        db,
        attendance
    )


@router.get(
    "/",
    response_model=List[AttendanceResponse]
)
def list_attendance(
    student_id: Optional[str] = None,
    date: Optional[DateType] = None,
    db: Session = Depends(get_db)
):
    return AttendanceService.get_attendance_records(
        db,
        student_id=student_id,
        attendance_date=date
    )


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    return AttendanceService.get_attendance_by_id(
        db,
        attendance_id
    )