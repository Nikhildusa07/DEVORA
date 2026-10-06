from datetime import date

from sqlalchemy import Column, Date, Integer, String, UniqueConstraint

from app.database import Base


class AttendanceModel(Base):
    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        String,
        index=True,
        nullable=False
    )

    student_name = Column(
        String,
        nullable=False
    )

    date = Column(
        Date,
        nullable=False,
        default=date.today
    )

    status = Column(
        String,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "date",
            name="uq_student_date"
        ),
    )
