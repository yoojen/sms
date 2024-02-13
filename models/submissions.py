from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base_model import Base, BaseModel


class Submission(Base, BaseModel):
    """Model for submission table in db storage"""
    __tablename__ = "submissions"
    cousre_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    dept_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.regno"), nullable=False)
    assign_id = Column(String(50), ForeignKey(
        "assignments.id"), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    file_path = Column(String(128), nullable=False)

    student = relationship("Student", back_populates="submissions")
    department = relationship("Department", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
