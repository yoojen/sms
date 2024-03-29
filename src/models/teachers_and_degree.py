from flask_login import UserMixin
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


class Teacher(UserMixin, BaseModel, Base):
    """Model for teacher table in db storage"""
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    tel = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(18), nullable=False)
    dob = Column(DateTime, nullable=False)
    citizenship = Column(String(20), nullable=False)
    staff_member = Column(Boolean, default=False)
    last_login = Column(DateTime)

    #  Many-To-Many relationship
    degree_association = relationship("TeacherDegree",
                                      back_populates="teacher",
                                      cascade='all, delete-orphan')
    degrees = association_proxy("degree_association", "degree")

    department_association = relationship(
        "TeacherDepartments", back_populates="teacher", cascade='all, delete-orphan')
    departments = association_proxy("department_association", "department")

    course_association = relationship(
        "TeacherCourse", back_populates="teacher", cascade='all, delete-orphan')
    courses = association_proxy("course_association", "course")

    #  One-To-Many relationship
    assignments = relationship(
        "Assignment", back_populates="teachers", cascade='all, delete-orphan')
    communications = relationship(
        "Communication", back_populates="teachers", cascade='all, delete-orphan')
    scored = relationship("Score", back_populates="teacher",
                          cascade='all, delete-orphan')
    materials = relationship(
        'Material', back_populates='teacher', cascade='all, delete-orphan')


class TeacherDegree(BaseModel, Base):
    """Model for teacher and degree assocition"""
    __tablename__ = "teachers_degree"
    id = Column(Integer, autoincrement=True, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    degree_id = Column(Integer, ForeignKey(
        "degrees.id", ondelete='CASCADE'), nullable=False)

    teacher = relationship("Teacher", back_populates="degree_association")
    degree = relationship("Degree", back_populates="teacher_association")


class Degree(BaseModel, Base):
    """Model for departments table in db storage"""
    __tablename__ = "degrees"
    id = Column(Integer, autoincrement=True, primary_key=True)
    degree_name = Column(String(10), nullable=False, unique=True)

    teacher_association = relationship(
        "TeacherDegree", back_populates="degree",
        cascade='all, delete-orphan')
    teachers = association_proxy("teacher_association", "teacher")
