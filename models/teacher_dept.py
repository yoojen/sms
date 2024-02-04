from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel


class TeacherDepartments(Base, BaseModel):
    """Model for teacher_departments table in db storage"""
    __tablename__ = "teacher_departments"
    teaceher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    dept_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    date_assigned = Column(DateTime, nullable=False)

    department = relationship(
        "Department", back_populates="teacher_association")
    teacher = relationship("Teacher", back_populates="department_association")
