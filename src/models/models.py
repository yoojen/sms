from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.associationproxy import association_proxy
from . import db


class BaseModel():
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def to_dict(self):
        obj = self.__dict__

        if obj.get("_sa_instance_state", None):
            del obj["_sa_instance_state"]
        return obj


class Assignment(BaseModel, db.Model):
    """Model for assignments table in db storage"""
    __tablename__ = "assignments"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='SET NULL'), nullable=True, unique=False)
    dept_id: Mapped[str] = mapped_column(ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False, unique=False)
    course_id: Mapped[str] = mapped_column(ForeignKey(
        "courses.course_code"), nullable=False, unique=False)
    assign_title: Mapped[str] = mapped_column(nullable=False)
    year_of_study: Mapped[int] = mapped_column(nullable=False)
    due_date: Mapped[datetime] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=False)
    submitted: Mapped[int] = mapped_column(default=0, nullable=True)

    # One-To-Many relationship
    teachers = relationship(
        "Teacher", back_populates="assignments")
    submissions = relationship(
        "Submission", back_populates="assignment", cascade='all, delete-orphan')

    department = relationship("Department", back_populates='assignments')
    course = relationship("Course", back_populates="assignments")


class Communication(BaseModel, db.Model):
    """Model for communications table in db storage"""
    __tablename__ = "communications"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[str] = mapped_column(ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    dept_id: Mapped[str] = mapped_column(ForeignKey("departments.dept_code",
                                                    ondelete='CASCADE'), nullable=False)
    year_of_study: Mapped[int] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)

    #  One-To-Many relationship
    teachers = relationship("Teacher", back_populates="communications")
    departments = relationship("Department", back_populates="communications")


class Department(BaseModel, db.Model):
    """Model for departments table in db storage"""
    __tablename__ = "departments"
    dept_code: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    dept_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    duration: Mapped[int] = mapped_column(nullable=False)
    trimester_or_semester: Mapped[str] = mapped_column(nullable=False)
    credits: Mapped[int] = mapped_column(nullable=False)
    n_teachers: Mapped[int] = mapped_column(nullable=True)
    hod: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='SET NULL'))

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
    scores = relationship(
        "Score", back_populates='department', cascade='delete, delete-orphan')
    students = relationship(
        "Student", back_populates="department")
    assignments = relationship(
        "Assignment", back_populates="department", cascade='delete, delete-orphan')


class DepartmentCourse(BaseModel, db.Model):
    """Model for departments_courses table in db storage"""
    __tablename__ = "department_course"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    dept_id: Mapped[str] = mapped_column(ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    date_assigned: Mapped[datetime] = mapped_column(nullable=False)

    course = relationship("Course", back_populates="department_association")
    department = relationship(
        "Department", back_populates="course_association")


class Course(BaseModel, db.Model):
    """Model for courses table in db storage"""
    __tablename__ = "courses"
    course_code: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    course_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    credits: Mapped[int] = mapped_column(nullable=False)
    year_of_study: Mapped[int] = mapped_column(nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey(
        "admins.id", ondelete="SET NULL"))
    description: Mapped[str] = mapped_column(nullable=True)

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
    creator = relationship("Admin", back_populates='courses')

    materials = relationship(
        "Material", back_populates='course', cascade='delete, delete-orphan')
    assignments = relationship(
        "Assignment", back_populates="course", cascade='delete, delete-orphan')


class Material(BaseModel, db.Model):
    """Model for materials table in db storage"""
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    course_code: Mapped[str] = mapped_column(ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    teacher_id: Mapped[str] = mapped_column(ForeignKey(
        "teachers.id", ondelete='SET NULL'))
    description: Mapped[str]
    link: Mapped[str] = mapped_column(nullable=False)

    department_association = relationship(
        "MaterialDepartments", back_populates="material", cascade='all, delete-orphan')
    departments = association_proxy("department_association", "department")

    teacher = relationship('Teacher', back_populates='materials')

    course = relationship("Course", back_populates="materials")


class MaterialDepartments(BaseModel, db.Model):
    """Model for materials_departments table in db storage"""
    __tablename__ = "material_department"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey(
        "materials.id", ondelete='CASCADE'), nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    date_uploaded: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), nullable=False)

    department = relationship(
        "Department", back_populates="material_association")
    material = relationship(
        "Material", back_populates="department_association")


class Role(BaseModel, db.Model):
    """Model for roles table in db storage"""
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    role_name: Mapped[str] = mapped_column(nullable=False)

    admins_association = relationship(
        "RoleAdmin", back_populates="role", cascade='delete, delete-orphan')
    admins = association_proxy("admins_association", "admin")


class RoleAdmin(BaseModel, db.Model):
    """Model for user_roles table in db storage"""
    __tablename__ = "roles_admin"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey(
        "admins.id", ondelete='CASCADE'), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey(
        "roles.id", ondelete='CASCADE'), nullable=False)
    date_granted: Mapped[datetime] = mapped_column(nullable=False)

    admin = relationship("Admin", back_populates="roles_association")
    role = relationship("Role", back_populates="admins_association")


class Admin(BaseModel, db.Model):
    """Model for admins table in db storage"""
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    dob: Mapped[datetime] = mapped_column(nullable=False)
    tel: Mapped[str] = mapped_column(nullable=False)
    citizenship: Mapped[str] = mapped_column(nullable=False)
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    roles_association = relationship(
        "RoleAdmin", back_populates="admin", cascade='delete,delete-orphan')
    roles = association_proxy("roles_association", "role")

    courses = relationship('Course', back_populates='creator')

    def get_id(self):
        return self.email


class Score(BaseModel, db.Model):
    """Model for scores table in db storage"""
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='SET NULL'))
    student_id: Mapped[int] = mapped_column(ForeignKey(
        "students.regno", ondelete='CASCADE'), nullable=False)
    dept_id: Mapped[str] = mapped_column(ForeignKey(
        'departments.dept_code', ondelete='CASCADE'), nullable=False)
    course_code: Mapped[str] = mapped_column(ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    assign_score: Mapped[int] = mapped_column(nullable=True)
    cat_score: Mapped[int] = mapped_column(nullable=True)
    exam_score: Mapped[int] = mapped_column(nullable=True)

    #  One-To-Many relationship
    student = relationship("Student", back_populates="scores")
    department = relationship("Department", back_populates='scores')
    teacher = relationship("Teacher", back_populates="scored")
    course = relationship("Course", back_populates="scores")


class Student(BaseModel, db.Model):
    """Model for students table in db storage"""
    __tablename__ = "students"
    regno: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    dob: Mapped[datetime] = mapped_column(nullable=False)
    tel: Mapped[str] = mapped_column(nullable=False)
    dept_id: Mapped[str] = mapped_column(ForeignKey(
        "departments.dept_code", ondelete='SET NULL'))
    year_of_study: Mapped[int] = mapped_column(nullable=False)
    sponsorship: Mapped[str] = mapped_column(nullable=True)
    citizenship: Mapped[str] = mapped_column(nullable=False)
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    scores = relationship("Score", back_populates="student",
                          cascade='delete, delete-orphan')
    submissions = relationship(
        "Submission", back_populates="student", cascade='delete, delete-orphan')
    department = relationship("Department", back_populates="students")

    # overidding get_id flask_login method
    def get_id(self):
        return self.regno


class Submission(BaseModel, db.Model):
    """Model for submission table in db storage"""
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey(
        "students.regno", ondelete='CASCADE'), nullable=False)
    assign_id: Mapped[int] = mapped_column(ForeignKey(
        "assignments.id", ondelete='CASCADE'), nullable=False)
    year_of_study: Mapped[int] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)

    student = relationship(
        "Student", back_populates="submissions")
    assignment = relationship(
        "Assignment", back_populates="submissions")


class TeacherCourse(BaseModel, db.Model):
    """Model for teacher_courses table in db storage"""
    __tablename__ = "teacher_courses"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    course_code: Mapped[str] = mapped_column(ForeignKey(
        "courses.course_code", ondelete='CASCADE'), nullable=False)
    date_assigned: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow())

    course = relationship("Course", back_populates="teacher_association")
    teacher = relationship("Teacher", back_populates='course_association')


class TeacherDepartments(BaseModel, db.Model):
    """Model for teacher_departments table in db storage"""
    __tablename__ = "teacher_departments"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    dept_id: Mapped[str] = mapped_column(ForeignKey(
        "departments.dept_code", ondelete='CASCADE'), nullable=False)
    date_assigned: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)

    department = relationship(
        "Department", back_populates="teacher_association")
    teacher = relationship("Teacher", back_populates="department_association")


class Teacher(BaseModel, db.Model):
    """Model for teacher table in db storage"""
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    tel: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    dob: Mapped[datetime] = mapped_column(nullable=False)
    citizenship: Mapped[str] = mapped_column(nullable=False)
    staff_member: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[datetime] = mapped_column(nullable=True)

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


class TeacherDegree(BaseModel, db.Model):
    """Model for teacher and degree assocition"""
    __tablename__ = "teachers_degree"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        "teachers.id", ondelete='CASCADE'), nullable=False)
    degree_id: Mapped[int] = mapped_column(ForeignKey(
        "degrees.id", ondelete='CASCADE'), nullable=False)

    teacher = relationship("Teacher", back_populates="degree_association")
    degree = relationship("Degree", back_populates="teacher_association")


class Degree(BaseModel, db.Model):
    """Model for departments table in db storage"""
    __tablename__ = "degrees"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    degree_name: Mapped[str] = mapped_column(nullable=False, unique=True)

    teacher_association = relationship(
        "TeacherDegree", back_populates="degree",
        cascade='all, delete-orphan')
    teachers = association_proxy("teacher_association", "teacher")
