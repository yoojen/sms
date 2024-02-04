from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base_model import Base, BaseModel


class Score(Base, BaseModel):
    """Model for scores table in db storage"""
    __tablename__ = "scores"
    assign_score = Column(Integer)
    cat_score = Column(Integer)
    exam_score = Column(Integer)
    teacher_id = Column(String(50), ForeignKey("teachers.id"))
    student_id = Column(Integer, ForeignKey("students.regno"), nullable=False)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
