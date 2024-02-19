from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Score(BaseModel, Base):
    """Model for scores table in db storage"""
    __tablename__ = "scores"
    id = Column(Integer, autoincrement=True, primary_key=True)
    teacher_id = Column(String(50), ForeignKey(
        "teachers.id"), nullable=False)
    student_id = Column(Integer, ForeignKey(
        "students.regno", ondelete='CASCADE'), nullable=False)
    dept_id = Column(String(10), ForeignKey(
        'departments.dept_code', ondelete='CASCADE'), nullable=False)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    assign_score = Column(Integer)
    cat_score = Column(Integer)
    exam_score = Column(Integer)

    #  One-To-Many relationship
    student = relationship("Student", back_populates="scores")
    department = relationship("Department", back_populates='scores')
    teacher = relationship("Teacher", back_populates="scored")
    course = relationship("Course", back_populates="scores")
