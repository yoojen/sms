from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Assignment(BaseModel, Base):
    """Model for assignments table in db storage"""
    __tablename__ = "assignments"
    id = Column(Integer, autoincrement=True, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    dept_id = Column(String(10), ForeignKey(
        "departments.dept_code"), nullable=False)
    course_id = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    assign_title = Column(String(50), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    due_date = Column(DateTime)
    description = Column(String(1000))
    link = Column(String(128), nullable=False)

    # One-To-Many relationship
    teachers = relationship(
        "Teacher", back_populates="assignments")
    submissions = relationship(
        "Submission", back_populates="assignment", cascade='all, delete-orphan')
