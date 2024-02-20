from models.courses_departments import Course
from api.v1.views import course_blueprint
from api.engine import db
from flask import jsonify


@course_blueprint.route('/courses', strict_slashes=False)
def courses():
    """returns all courses objects from the db"""
    courses_list = []
    courses = db.get_all_object(Course)
    for course in courses:
        courses_list.append(course.to_json())
    return jsonify({"courses": courses_list})


@course_blueprint.route('/courses/<code>', strict_slashes=False)
def courses_by_code(code):
    course = db.get_by_id(Course, code)
    if course:
        course.to_json()
    return jsonify({"course": course})
