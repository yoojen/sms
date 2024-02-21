from models.courses_departments import Course, Department, DepartmentCourse
from api.v1.views import course_blueprint
from api.engine import db
import requests
from flask import jsonify, request

BASE_URL = 'http://localhost:5000/api/v1'


@course_blueprint.route('/courses', methods=['GET'], strict_slashes=False)
def courses():
    """returns all courses objects from the db"""
    """
    courses: [
        0: [{
        departments: [list of all departments that has course],
        materials: [list of all materials related to course],
        teachers: [all teachers who teach this course],
        assignment: [list of all assignments],
        creater: [who created the course]
        }],

    ]
    """
    new_obj = {}
    all_courses = []
    courses = db.get_all_object(Course)
    for course in courses:
        print(course)
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in course.departments]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in course.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in course.teachers]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in course.assignments] yet to be implemented
        creator = f'{BASE_URL}/creators/{course.creator.id}'

        for k, v in course.to_json().items():
            if k in ['course_code', 'year_of_study', 'end_date', 'description',
                     'created_at', 'course_name', 'credits', 'start_date',
                     'created_by', 'updated_at']:
                new_obj[k] = v
        new_obj['departments'] = departments
        new_obj['materials'] = materials
        new_obj['teachers'] = teachers
        new_obj['creator'] = creator
        all_courses.append(new_obj)
        new_obj = {}
    return jsonify({"courses": all_courses})


@course_blueprint.route('/courses/<code>', methods=['GET'], strict_slashes=False)
def courses_by_code(code):
    new_obj = {}
    course = db.get_by_id(Course, code)
    if course:
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in course.departments]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in course.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in course.teachers]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in course.assignments] yet to be implemented
        creator = f'{BASE_URL}/creators/{course.creator.id}'

        for k, v in course.to_json().items():
            if k in ['course_code', 'year_of_study', 'end_date', 'description',
                     'created_at', 'course_name', 'credits', 'start_date',
                     'created_by', 'updated_at']:
                new_obj[k] = v
        new_obj['departments'] = departments
        new_obj['materials'] = materials
        new_obj['teachers'] = teachers
        new_obj['creator'] = creator

        # handling url args
        if request.args:
            if 'score' == list(request.args)[0]:
                course_scores = find_course_scores(code)
                return jsonify({"scores": {"course": course.course_code,
                                           "score": course_scores}})
            elif 'departments' == list(request.args)[0]:
                dept_with_crs = find_department_with_course(code)
                return jsonify({"departments": {"course": course.course_code,
                                                "departments": dept_with_crs}})
            elif 'materials' == list(request.args)[0]:
                crs_materials = find_crs_materials(code)
                return jsonify({"materials": {"course": course.course_code,
                                              "materials": crs_materials}})
            else:
                return jsonify({"message":
                                f"{list(request.args)[0]} not implemented"})

    return jsonify({"course": new_obj})


def find_course_scores(code):
    all_scores = []
    course = course = db.get_by_id(Course, code)
    scores = course.scores
    for score in scores:
        all_scores.append(score.to_json())
    return all_scores


def find_department_with_course(code):
    all_depts = []
    course = course = db.get_by_id(Course, code)
    depts = course.departments
    for dept in depts:
        all_depts.append(dept.to_json())
    return all_depts


def find_crs_materials(code):
    all_materials = []
    course = course = db.get_by_id(Course, code)
    materials = course.materials
    for mat in materials:
        all_materials.append(mat.to_json())
    return all_materials
