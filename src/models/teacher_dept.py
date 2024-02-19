from sqlalchemy import Column, String, ForeignKey, DateTime
from uuid import uuid4
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class TeacherDepartments(BaseModel, Base):
    """Model for teacher_departments table in db storage"""
    __tablename__ = "teacher_departments"
    id = Column(String(30), default=uuid4(), primary_key=True)
    teaceher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    dept_id = Column(String(10), ForeignKey(
        "departments.dept_code"), nullable=False)
    date_assigned = Column(DateTime, nullable=False)

    department = relationship(
        "Department", back_populates="teacher_association")
    teacher = relationship("Teacher", back_populates="department_association")