from sqlalchemy import (Column,
                        String,
                        Boolean,
                        DateTime,
                        ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import BaseModel, Base


class Teacher(BaseModel, Base):
    """Model for teacher table in db storage"""
    __tablename__ = "teachers"
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    email = Column(String(50), nullable=False)
    password = Column(String(18), nullable=False)
    dob = Column(DateTime, nullable=False)
    staff_member = Column(Boolean, default=False)
    last_login = Column(DateTime)

    #  Many-To-Many relationship
    degree_association = relationship(
        "TeacherDegree", back_populates="teacher")
    degrees = association_proxy("degree_association", "degree")

    department_association = relationship(
        "TeacherDepartments", back_populates="teacher")
    departments = association_proxy("department_association", "department")

    course_association = relationship(
        "TeacherCourse", back_populates="teacher")
    courses = association_proxy("course_association", "course")

    #  One-To-Many relationship
    assignments = relationship("Assignment", back_populates="teachers")
    communications = relationship("Communication", back_populates="teachers")
    scored = relationship("Score", back_populates="teacher")


class TeacherDegree(BaseModel, Base):
    """Model for teacher and degree assocition"""
    __tablename__ = "teachers_degree"
    teacher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    degree_id = Column(String(50), ForeignKey("degrees.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="degree_association")
    degree = relationship("Degree", back_populates="teacher_association")


class Degree(BaseModel, Base):
    """Model for departments table in db storage"""
    __tablename__ = "degrees"
    degree_name = Column(String(10), nullable=False)

    teacher_association = relationship(
        "TeacherDegree", back_populates="degree")
    teachers = association_proxy("teacher_association", "teacher")
