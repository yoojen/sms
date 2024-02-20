from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import BaseModel, Base
from uuid import uuid4


class Department(BaseModel, Base):
    """Model for departments table in db storage"""
    __tablename__ = "departments"
    dept_code = Column(String(10), primary_key=True, nullable=False)
    dept_name = Column(String(50), nullable=False, unique=True)
    duration = Column(Integer, nullable=False)
    trimester_or_semester = Column(String(10), nullable=False)
    credits = Column(Integer, nullable=False)
    n_teachers = Column(Integer)
    hod = Column(String(50), ForeignKey(
        "teachers.id", ondelete='SET NULL'), nullable=False)

    # Many-To-Many relationship
    course_association = relationship(
        "DepartmentCourse", back_populates="department", cascade='all, delete-orphan')
    courses = association_proxy("course_association", "course")

    teacher_association = relationship(
        "TeacherDepartments", back_populates="department", cascade='all, delete-orphan')
    teachers = association_proxy("teacher_association", "teacher")

    material_association = relationship(
        "MaterialDepartments", back_populates="department", cascade='all, delete-orphan')
    materials = association_proxy("material_association", "material")

    # One-To-Many relationship
    communications = relationship(
        "Communication", back_populates="departments", cascade='delete, delete-orphan')
    submissions = relationship(
        "Submission", back_populates="department", cascade='delete, delete-orphan')
    scores = relationship(
        "Score", back_populates='department', cascade='delete, delete-orphan')
    students = relationship(
        "Student", back_populates="department")


class DepartmentCourse(BaseModel, Base):
    """Model for departments_courses table in db storage"""
    id = Column(Integer, autoincrement=True, primary_key=True)
    __tablename__ = "departments_courses"
    dept_id = Column(String(10), ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    course_id = Column(String(10), ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    date_assigned = Column(DateTime, nullable=False)

    course = relationship("Course", back_populates="department_association")
    department = relationship(
        "Department", back_populates="course_association")


class Course(BaseModel, Base):
    """Model for courses table in db storage"""
    __tablename__ = "courses"
    course_code = Column(String(10), primary_key=True, nullable=False)
    course_name = Column(String(50), nullable=False, unique=True)
    credits = Column(Integer, nullable=False)
    year_of_study = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(String(50), ForeignKey(
        "admins.id", ondelete="SET NULL"), nullable=False)

    #  Many-To-Many relationship
    department_association = relationship(
        "DepartmentCourse", back_populates="course", cascade='all, delete-orphan')
    departments = association_proxy("department_association", "department")

    teacher_association = relationship(
        "TeacherCourse", back_populates="course", cascade='all, delete-orphan')
    teachers = association_proxy("teacher_association", "teacher")

    #  One-To-Many relationship
    scores = relationship("Score", back_populates="course",
                          cascade='all, delete-orphan')
