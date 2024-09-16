from flask_login import current_user, login_required
from models.models import (
        Course, Department, Admin,
        Score, Student, Teacher
    )
from api.v1.views import score_blueprint
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound


BASE_URL = 'http://localhost:5000/api/v1'


@score_blueprint.route('/scores', methods=['GET'], strict_slashes=False)
@login_required
def scores():
    """returns all Score objects from the db"""

    new_obj = {}
    all_scores = []
    scores = db_controller.get_all_object(Score)
    for score in scores:
        teacher = score.teacher.to_json() if score.teacher else None
        course = score.course.to_json()
        department = score.department.to_json()
        students = score.student.to_json()

        for k, v in score.to_json().items():
            if k in ['id', 'teacher_id', 'student_id',  'dept_id', 'course_code', 'assign_score',
                     'cat_score', 'exam_score', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['course'] = course
        new_obj['teacher'] = teacher
        new_obj['department'] = department
        new_obj['students'] = students

        if isinstance(current_user, Student):
            if score.student_id == current_user.regno:
                all_scores.append(new_obj)
        if isinstance(current_user, Admin):
            all_scores.append(new_obj)
        if isinstance(current_user, Teacher):
            if score.teacher_id == current_user.id:
                all_scores.append(new_obj)
        new_obj = {}
    return jsonify({"scores": all_scores}), 200


@score_blueprint.route('/scores/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def single_score(id):
    """returns single Score objects from the db_controller"""
    holder_old = {}
    new_obj = {}
    score = db_controller.get_by_id(Score, id)
    if score:
        teacher = score.teacher.to_json() if score.teacher else None
        course = score.course.to_json()
        department = score.department.to_json()
        students = score.student.to_json()

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(score, args_dict)
            return jsonify([data]), status_code

        for k, v in score.to_json().items():
            if k in ['id', 'teacher_id', 'student_id', 'dept_id',
                     'course_code', 'assign_score',
                     'cat_score', 'exam_score', 'created_at', 'updated_at']:
                holder_old[k] = v
        holder_old['course'] = course
        holder_old['teacher'] = teacher
        holder_old['department'] = department
        holder_old['students'] = students
        if isinstance(current_user, Student):
            if score.student_id == current_user.regno:
                new_obj = holder_old
        if isinstance(current_user, Admin):
            new_obj = holder_old
        if isinstance(current_user, Teacher):
            if score.teacher_id == current_user.id:
                new_obj = holder_old

        return jsonify({"scores": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@score_blueprint.route('/scores', methods=['POST'],
                       strict_slashes=False)
@login_required
def create_score():
    """function that handles creation endpoint for Score instance"""
    data = dict(request.form)
    if isinstance(current_user, Student):
        abort(403)

    if isinstance(current_user, Admin):
        data['teacher_id'] = None

    student = db_controller.get_by_id(Student, int(data.get('student_id')))
    dept = db_controller.get_by_id(Department, data['dept_id'])
    course = db_controller.get_by_id(Course, data['course_code'])

    if not student:
        return jsonify(ERROR='Student not exists')
    if not dept:
        return jsonify(ERROR='Department not exists')
    if not course:
        return jsonify(ERROR='Course not exists')
    if course not in dept.courses:
        return jsonify(ERROR='Department and course conflict')

    # check if teacher has access to dept & course
    if isinstance(current_user, Teacher):
        if set([dept]) & set(current_user.departments):
            data['teacher_id'] = int(current_user.id)
        else:
            abort(403)
    try:
        # check if it exists
        find_score = db_controller.search(Score, student_id=int(data.get('student_id')),
                               dept_id=data.get('dept_id'),
                               course_code=data.get('course_code'))
        if find_score:
            return jsonify(error="Score already exist"), 409
        created = db_controller.create_object(Score(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "created_by": created.id}), 201


@score_blueprint.route('/scores/<int:id>', methods=['PUT'],
                       strict_slashes=False)
@login_required
def update_score(id):
    """ function that handles update endpoint for Score instance"""
    if isinstance(current_user, Student):
        abort(403)

    if isinstance(current_user, Teacher):
        score = db_controller.get_by_id(Score, int(id))
        if score.teacher != current_user:
            abort(403)
    try:
        data = dict(request.form)
        updated = db_controller.update(Score, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@score_blueprint.route('/scores/<int:id>', methods=['DELETE'],
                       strict_slashes=False)
@login_required
def delete_score(id):
    """function for delete endpoint, it handles Score deletion"""
    if isinstance(current_user, Student):
        abort(403)

    if isinstance(current_user, Teacher):
        score = db_controller.get_by_id(Score, int(id))
        if score.teacher != current_user:
            abort(403)
    try:
        db_controller.delete(Score, id)
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
