from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base
from flask_login import UserMixin


class Student(UserMixin, BaseModel, Base):
    """Model for students table in db storage"""
    __tablename__ = "students"
    regno = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(18), nullable=False)
    dob = Column(DateTime, nullable=False)
    tel = Column(String(20), nullable=False)
    dept_id = Column(String(50), ForeignKey(
        "departments.dept_code", ondelete='SET NULL'))
    year_of_study = Column(Integer, nullable=False)
    sponsorship = Column(String(50))
    citizenship = Column(String(50), nullable=False)
    last_login = Column(DateTime)

    scores = relationship("Score", back_populates="student",
                          cascade='delete, delete-orphan')
    submissions = relationship(
        "Submission", back_populates="student", cascade='delete, delete-orphan')
    department = relationship("Department", back_populates="students")

    # overidding get_id flask_login method
    def get_id(self):
        return self.regno
