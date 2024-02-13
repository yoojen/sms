from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import Base, BaseModel


class Material(Base, BaseModel):
    """Model for materials table in db storage"""
    __tablename__ = "materials"
    course_code = Column(String(10), ForeignKey(
        "courses.course_code"), nullable=False)
    teacher_id = Column(String(50), ForeignKey("teachers.id"), nullable=False)
    year_of_study = Column(Integer, nullable=False)
    description = Column(String(256))
    file_path = Column(String(128), nullable=False)

    department_association = relationship(
        "MaterialDepartments", back_populates="material")
    departments = association_proxy("department_association", "department")


class MaterialDepartments(Base, BaseModel):
    """Model for materials_departments table in db storage"""
    __tablename__ = "materials_departments"
    material_id = Column(String(50), ForeignKey(
        "materials.id"), nullable=False)
    department_id = Column(String(50), ForeignKey(
        "departments.id"), nullable=False)
    date_uploaded = Column(DateTime, nullable=False)

    department = relationship(
        "Department", back_populates="material_association")
    material = relationship(
        "Material", back_populates="department_association")
