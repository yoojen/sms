from sqlalchemy import (Column,
                        Integer,
                        String,
                        Boolean,
                        DateTime,
                        ForeignKey)
from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import BaseModel, Base


class Teacher(BaseModel, Base):
    """Model for teacher table in db storage"""
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, nullable=False)
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
    assignments = relationship(
        "Assignment", back_populates="teachers", cascade='all, delete-orphan')
    communications = relationship(
        "Communication", back_populates="teachers", cascade='all, delete-orphan')
    scored = relationship("Score", back_populates="teacher",
                          cascade='all, delete-orphan')


class TeacherDegree(BaseModel, Base):
    """Model for teacher and degree assocition"""
    __tablename__ = "teachers_degree"
    id = Column(String(30), default=uuid4(), primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    degree_id = Column(Integer, ForeignKey("degrees.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="degree_association")
    degree = relationship("Degree", back_populates="teacher_association")


class Degree(BaseModel, Base):
    """Model for departments table in db storage"""
    __tablename__ = "degrees"
    id = Column(Integer, autoincrement=True, primary_key=True)
    degree_name = Column(String(10), nullable=False)

    teacher_association = relationship(
        "TeacherDegree", back_populates="degree")
    teachers = association_proxy("teacher_association", "teacher")
