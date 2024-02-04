from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import Base, BaseModel


class Department(Base, BaseModel):
    """Model for departments table in db storage"""
    __tablename__ = "departments"
    dept_code = Column(String(10), primary_key=True, nullable=False)
    dept_name = Column(String(50), nullable=False)
    duration = Column(Integer, nullable=False)
    trimester_or_semester = Column(String(10), nullable=False)
    credits = Column(Integer, nullable=False)
    n_teachers = Column(Integer)
    hod = Column(String(50), ForeignKey("teachers.id"), nullable=False)

    course_association = relationship(
        "DepartmentCourse", back_populates="department")
    courses = association_proxy("course_association", "course")

    teacher_association = relationship(
        "TeacherDepartments", back_populates="department")
    teachers = association_proxy("teacher_association", "teacher")

    material_association = relationship(
        "MaterialDepartments", back_populates="department")
    materials = association_proxy("material_association", "material")


class DepartmentCourse(Base, BaseModel):
    """Model for departments_courses table in db storage"""
    __tablename__ = "departments_courses"
    dept_id = Column(String(50), ForeignKey(
        "departments.dept_code"), nullable=False)
    course_id = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    date_assigned = Column(DateTime, nullable=False)

    course = relationship("Course", back_populates="department_association")
    department = relationship(
        "Department", back_populates="course_association")


class Course(Base, BaseModel):
    """Model for courses table in db storage"""
    __tablename__ = "courses"
    course_code = Column(String(10), primary_key=True, nullable=False)
    course_name = Column(String(50), nullable=False)
    credits = Column(Integer, nullable=False)
    year_of_study = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(String(50), ForeignKey("admins.id"), nullable=False)

    department_association = relationship(
        "DepartmentCourse", back_populates="course")
    departments = association_proxy("department_association", "department")

    teacher_association = relationship(
        "TeacherCourse", back_populates="course")
    teachers = association_proxy("teacher_association", "teacher")
