from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from base_model import Base, BaseModel


class Schedule(Base, BaseModel):
    """Model for schedule table in db storage"""
    __tablename__ = "schedules"
    description = Column(String(256), nullable=False)
    teacher_id = Column(String(50), ForeignKey('teachers.id'), nullable=False)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
