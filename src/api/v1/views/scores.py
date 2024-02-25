from models.courses_departments import Course, Department
from models.scores import Score
from api.v1.views import score_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime
from models.students import Student

from models.teachers_and_degree import Teacher


BASE_URL = 'http://localhost:5000/api/v1'


@score_blueprint.route('/scores', methods=['GET'], strict_slashes=False)
def scores():
    """returns all Score objects from the db"""

    new_obj = {}
    all_scores = []
    scores = db.get_all_object(Score)
    for score in scores:
        teacher = f'{BASE_URL}/teachers/{score.teacher.id}'
        course = f'{BASE_URL}/courses/{ score.course.course_code}'
        department = f'{BASE_URL}/departments/{score.department.dept_code}'
        students = f'{BASE_URL}/students/{score.student.regno}'

        for k, v in score.to_json().items():
            if k in ['id', 'teacher_id', 'student_id',  'dept_id', 'course_code', 'assign_score',
                     'cat_score', 'exam_score', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['course'] = course
        new_obj['teacher'] = teacher
        new_obj['department'] = department
        new_obj['students'] = students
        all_scores.append(new_obj)
        new_obj = {}
    return jsonify({"scores": all_scores}), 200


@score_blueprint.route('/scores/<int:id>', methods=['GET'], strict_slashes=False)
def single_score(id):
    """returns single Score objects from the db"""

    new_obj = {}
    score = db.get_by_id(Score, id)
    if score:
        teacher = f'{BASE_URL}/teachers/{score.teacher.id}'
        course = f'{BASE_URL}/courses/{ score.course.course_code}'
        department = f'{BASE_URL}/departments/{score.department.dept_code}'
        students = f'{BASE_URL}/students/{score.student.regno}'

        for k, v in score.to_json().items():
            if k in ['id', 'teacher_id', 'student_id', 'dept_id', 'course_code', 'assign_score',
                     'cat_score', 'exam_score', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['course'] = course
        new_obj['teacher'] = teacher
        new_obj['department'] = department
        new_obj['students'] = students

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(score, args_dict)
            return jsonify([data]), status_code
        return jsonify({"scores": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@score_blueprint.route('/scores', methods=['POST'],
                       strict_slashes=False)
def create_score():
    """function that handles creation endpoint for Score instance"""
    data = dict(request.form)
    teacher = db.get_by_id(Teacher, data['teacher_id'])
    student = db.get_by_id(Student, data['student_id'])
    dept = db.get_by_id(Department, data['dept_id'])
    course = db.get_by_id(Course, data['course_code'])

    if not teacher:
        return jsonify(ERROR='Teacher not exists')
    if not student:
        return jsonify(ERROR='Student not exists')
    if not dept:
        return jsonify(ERROR='Department not exists')
    if not course:
        return jsonify(ERROR='Course not exists')
    try:
        # check if it exists
        find_Score = db.get_by_id(Score, data.get('id'))
        if find_Score:
            return jsonify(error="Score already exist"), 409
        created = db.create_object(Score(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "created_by": created.teacher.email}), 201


@score_blueprint.route('/scores/<int:id>', methods=['PUT'],
                       strict_slashes=False)
def update_score(id):
    """ function that handles update endpoint for Score instance"""
    try:
        data = dict(request.form)
        updated = db.update(Score, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@score_blueprint.route('/scores/<int:id>', methods=['DELETE'],
                       strict_slashes=False)
def delete_score(id):
    """function for delete endpoint, it handles Score deletion"""

    try:
        db.delete(Score, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted score"), 200

# helpers


def find_score_student(score):
    """Find student associated with score"""
    return score.student.to_json()


def find_score_department(score):
    """find department that are associated with score"""
    return score.department.to_json()


def find_score_teacher(score):
    """find teacher that are associated with the score"""
    return score.teacher.to_json()


def find_score_course(score):
    """find course that are associated with the score"""
    return score.course.to_json()


def args_handler(score, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented"), 400
    if args.get('department') == 'true':
        depts = find_score_department(score)
        status_code = 200
        return {"score": score.id,
                "departments": depts}, status_code
    elif args.get('teacher') == 'true':
        tchr = find_score_teacher(score)
        status_code = 200
        return {"score": score.id,
                "teacher": tchr}, status_code
    elif args.get('course') == 'true':
        crs = find_score_course(score)
        status_code = 200
        return {"score": score.id,
                "course": crs}, status_code
    elif args.get('student') == 'true':
        student = find_score_student(score)
        status_code = 200
        return {"score": score.id,
                "student": student}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
