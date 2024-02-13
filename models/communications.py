from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class Communication(Base, BaseModel):
    """Model for communications table in db storage"""
    __tablename__ = "communications"
    teacher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    dept_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    message = Column(String(1000), nullable=False)

    #  One-To-Many relationship
    teachers = relationship("Teacher", back_populates="communications")
    departments = relationship("Department", back_populates="communications")
