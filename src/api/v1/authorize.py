from flask_login import current_user
from api.engine import db
from models.courses_departments import Course, Department
from models.teachers_and_degree import Teacher
from models.teacher_course import TeacherCourse


def is_admin(self):
    objs = db.get_all_object(self.class_name)
    return objs


def is_teacher(teacher_id):
    tch = db.get_by_id(Teacher, teacher_id)
    return tch.departments


def is_student(self):
    pass


def find_dept(id):
    dept = db.get_by_id(Department, id)
    return dept


def find_course(id):
    crs = db.get_by_id(Course, id)
    return crs


def find_assoc(id):
    assoc = db.get_by_id(TeacherCourse, id)
    return assoc
