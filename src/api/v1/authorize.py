from flask_login import current_user
from models.models import Teacher, Department, Course, TeacherCourse
from api.engine import db_controller


def is_admin(self):
    objs = db_controller.get_all_object(self.class_name)
    return objs


def is_teacher(teacher_id):
    tch = db_controller.get_by_id(Teacher, teacher_id)
    return tch.departments


def is_student(self):
    pass


def find_dept(id):
    dept = db_controller.get_by_id(Department, id)
    return dept


def find_course(id):
    crs = db_controller.get_by_id(Course, id)
    return crs


def find_assoc(id):
    assoc = db_controller.get_by_id(TeacherCourse, id)
    return assoc
