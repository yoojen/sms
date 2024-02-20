from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base
from uuid import uuid4


class TeacherCourse(BaseModel, Base):
    """Model for teacher_courses table in db storage"""
    __tablename__ = "teacher_courses"
    id = Column(Integer, autoincrement=True, primary_key=True)
    teacher_id = Column(String(50), ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    date_assigned = Column(DateTime, nullable=False)

    course = relationship("Course", back_populates="teacher_association")
    teacher = relationship("Teacher", back_populates='course_association')
