from datetime import date as DateType

from pydantic import BaseModel, Field


class AttendanceBase(BaseModel):
    student_id: str = Field(...)
    student_name: str = Field(...)
    date: DateType = Field(default_factory=DateType.today)
    status: str = Field(...)


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True
