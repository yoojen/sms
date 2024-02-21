from models.courses_departments import Course, Department, DepartmentCourse
from api.v1.views import course_blueprint
from api.engine import db
from flask import jsonify

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


@course_blueprint.route('/courses/<code>', strict_slashes=False)
def courses_by_code(code):
    course = db.get_by_id(Course, code)
    if course:
        course = course.to_json()
    return jsonify({"course": course})
