from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Submission(BaseModel, Base):
    """Model for submission table in db storage"""
    __tablename__ = "submissions"
    id = Column(Integer, autoincrement=True, primary_key=True)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    dept_id = Column(String(10), ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey(
        "students.regno", ondelete='CASCADE'), nullable=False)
    assign_id = Column(Integer, ForeignKey(
        "assignments.id", ondelete='CASCADE'), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    link = Column(String(128), nullable=False)

    student = relationship(
        "Student", back_populates="submissions")
    department = relationship(
        "Department", back_populates="submissions")
    assignment = relationship(
        "Assignment", back_populates="submissions")
