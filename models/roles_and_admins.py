from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from models.base_model import BaseModel, Base


class Role(BaseModel, Base):
    """Model for roles table in db storage"""
    __tablename__ = "roles"
    role_name = Column(String(50), nullable=False)

    admins_association = relationship("RoleAdmin", back_populates="role")
    admins = association_proxy("admins_association", "admin")


class RoleAdmin(BaseModel, Base):
    """Model for user_roles table in db storage"""
    __tablename__ = "roles_admin"
    role_id = Column(String(50), ForeignKey("roles.id"), nullable=False)
    admin_id = Column(String(50), ForeignKey("admins.id"), nullable=False)
    date_granted = Column(String(50), nullable=False)

    admin = relationship("Admin", back_populates="roles_association")
    role = relationship("Role", back_populates="admins_association")


class Admin(BaseModel, Base):
    """Model for admins table in db storage"""
    __tablename__ = "admins"
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    email = Column(String(50), nullable=False)
    password = Column(String(18), nullable=False)
    dob = Column(DateTime, nullable=False)
    last_login = Column(DateTime)

    roles_association = relationship("RoleAdmin", back_populates="admin")
    roles = association_proxy("roles_association", "role")
