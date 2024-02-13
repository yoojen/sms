from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base_model import Base, BaseModel
from datetime import datetime, date


class Student(Base, BaseModel):
    """Model for students table in db storage"""
    __tablename__ = "students"
    regno = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    email = Column(String(50), nullable=False)
    password = Column(String(18), nullable=False)
    dob = Column(date, nullable=False)
    dept_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    sponsorship = Column(String(50))
    citizenship = Column(String(50), nullable=False)
    last_login = Column(datetime)

    scores = relationship("Score", back_populates="student")
    submissions = relationship("Submission", back_populates="student")
