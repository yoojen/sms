from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import BaseModel, Base


class Material(BaseModel, Base):
    """Model for materials table in db storage"""
    __tablename__ = "materials"
    id = Column(Integer, autoincrement=True, primary_key=True)
    course_code = Column(String(10), ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    teacher_id = Column(String(50), ForeignKey(
        "teachers.id", ondelete='SET NULL'), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    description = Column(String(256))
    link = Column(String(128), nullable=False)

    department_association = relationship(
        "MaterialDepartments", back_populates="material", cascade='all, delete-orphan')
    departments = association_proxy("department_association", "department")

    teacher = relationship('Teacher', back_populates='materials')

    course = relationship("Course", back_populates="materials")


class MaterialDepartments(BaseModel, Base):
    """Model for materials_departments table in db storage"""
    __tablename__ = "materials_departments"
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(
        "materials.id", ondelete='CASCADE'), nullable=False)
    department_id = Column(String(10), ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    date_uploaded = Column(DateTime, nullable=False)

    department = relationship(
        "Department", back_populates="material_association")
    material = relationship(
        "Material", back_populates="department_association")
