from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attendance import AttendanceModel
from app.schemas.attendance import AttendanceCreate


class AttendanceService:

    @staticmethod
    def record_attendance(
        db: Session,
        attendance_in: AttendanceCreate
    ) -> AttendanceModel:

        existing = (
            db.query(AttendanceModel)
            .filter(
                AttendanceModel.student_id == attendance_in.student_id,
                AttendanceModel.date == attendance_in.date
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Attendance for student "
                    f"{attendance_in.student_id} on date "
                    f"{attendance_in.date} is already recorded."
                )
            )

        db_attendance = AttendanceModel(
            student_id=attendance_in.student_id,
            student_name=attendance_in.student_name,
            date=attendance_in.date,
            status=attendance_in.status
        )

        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)

        return db_attendance

    @staticmethod
    def get_attendance_records(
        db: Session,
        student_id: Optional[str] = None,
        attendance_date: Optional[date] = None
    ) -> List[AttendanceModel]:

        query = db.query(AttendanceModel)

        if student_id:
            query = query.filter(
                AttendanceModel.student_id == student_id
            )

        if attendance_date:
            query = query.filter(
                AttendanceModel.date == attendance_date
            )

        return query.all()

    @staticmethod
    def get_attendance_by_id(
        db: Session,
        attendance_id: int
    ) -> AttendanceModel:

        attendance = (
            db.query(AttendanceModel)
            .filter(
                AttendanceModel.id == attendance_id
            )
            .first()
        )

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Attendance record with id "
                    f"{attendance_id} not found."
                )
            )

        return attendance
