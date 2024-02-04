from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel
from datetime import date


class Assignment(Base, BaseModel):
    """Model for assignments table in db storage"""
    __tablename__ = "assignments"
    teacher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    dept_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    course_id = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    assign_title = Column(String(50), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    due_date = Column(DateTime)
    description = Column(String(256))
