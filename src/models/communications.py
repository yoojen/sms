from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Communication(BaseModel, Base):
    """Model for communications table in db storage"""
    __tablename__ = "communications"
    id = Column(Integer, autoincrement=True, primary_key=True)
    teacher_id = Column(String(50), ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    dept_id = Column(String(10), ForeignKey("departments.dept_code",
                     ondelete='CASCADE'), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    message = Column(String(1000), nullable=False)

    #  One-To-Many relationship
    teachers = relationship("Teacher", back_populates="communications")
    departments = relationship("Department", back_populates="communications")
