from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Score(Base, BaseModel):
    """Model for scores table in db storage"""
    __tablename__ = "scores"
    teacher_id = Column(String(50), ForeignKey("teachers.id"))
    student_id = Column(Integer, ForeignKey("students.regno"), nullable=False)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    assign_score = Column(Integer)
    cat_score = Column(Integer)
    exam_score = Column(Integer)

    #  One-To-Many relationship
    student = relationship("Student", back_populates="scores")
    teacher = relationship("Teacher", back_populates="scored")
    course = relationship("Course", back_populates="scores")
