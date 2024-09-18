# from flask_login import current_user, login_required
from flask_jwt_extended import (
    current_user, jwt_required)
from models.models import Assignment, Student, Teacher, Department, Course, BaseModel
from api.v1.views import assignm_blueprint
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import datetime
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    current_user, jwt_required,
    get_jwt_identity)


BASE_URL = 'http://localhost:5000/api/v1'


@assignm_blueprint.route('/assignments', methods=['GET'], strict_slashes=False)
@jwt_required()
def assignments():
    """returns all Assignments objects from the db"""
    all_assignms = []
    # I'll work on different users
    if isinstance(current_user, Student):
        assignms = [assign for assign in current_user.department.assignments if assign.year_of_study ==
                    current_user.year_of_study]
    elif isinstance(current_user, Teacher):
        assignms = current_user.assignments
    else:
        assignms = db_controller.get_all_object(Assignment)
    for assignm in assignms:
        if assignm.due_date < datetime.now():
            continue
        all_assignms.append(assignm.to_dict())
    return jsonify({"assignments": all_assignms}), 200


@assignm_blueprint.route('/assignments/<int:id>', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def one_assignment(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    holder_obj = {}
    assignm = db_controller.get_by_id(Assignment, id)
    if assignm:
        ass_dept = assignm.department
        course = assignm.course.to_dict()
        teacher = assignm.teachers.to_dict()

        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in assignm.submissions]

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(assignm, args_dict)
            return jsonify(data), status_code
        for k, v in assignm.to_dict().items():
            if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                     'year_of_study', 'due_date', 'description', 'link',
                     'created_at', 'updated_at']:
                holder_obj[k] = v
        holder_obj['teacher'] = teacher
        holder_obj['course'] = course
        holder_obj['submissions'] = submissions
        if current_user.__tablename__ == 'admins':
            """display course based on admin credentials"""
            new_obj = holder_obj
        if current_user.__tablename__ == 'teachers':
            if assignm.teachers == current_user:
                new_obj = holder_obj

        if current_user.__tablename__ == 'students':
            if current_user.department == ass_dept and\
                    assignm.year_of_study == current_user.year_of_study:
                new_obj = holder_obj

        return jsonify({"assignment": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 200


@assignm_blueprint.route('/assignments/', methods=['POST'], strict_slashes=False)
@jwt_required(optional=True)
def create_assignments():
    """function that handles creation endpoint for Assignment instance"""
    user = current_user.__tablename__
    data = dict(request.form)

    teacher = db_controller.get_by_id(Teacher, data.get('teacher_id'))
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db_controller.get_by_id(Department, data.get('dept_id'))
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404
    course = db_controller.get_by_id(Course, data.get('course_id'))
    if not course:
        return jsonify(ERROR='Course does not exists'), 404
    if user == 'admins' or user == 'teachers':
        try:
            data['due_date'] = datetime.strptime(
                data.get('due_date'), BaseModel.DATE_FORMAT)
            # check if it exists
            find_dept = db_controller.search(Assignment, id=data.get('id'),
                                             dept_id=data.get('dept_id'),
                                             teacher_id=data.get('teacher_id'),
                                             assign_title=data.get('assign_title'))
            if find_dept:
                return jsonify(error="Assignment already exist")
            created = db_controller.create_object(Assignment(**data))
        except Exception as e:
            return jsonify({"message": "Not created", "error": str(e)}), 400
        return jsonify({"message": "Successfully created",
                        "title": created.assign_title}), 201
    return jsonify(ERROR='Admins only')


@assignm_blueprint.route('/assignments/<int:id>', methods=['PUT'], strict_slashes=False)
@jwt_required(optional=True)
def update_assignment(id):
    """ function that handles update endpoint for Assignment instance"""
    user = current_user.__tablename__
    if user == 'students':
        abort(403)
    if user == 'teachers':
        assign = db_controller.get_by_id(Assignment, id)
        if assign.teachers:
            if assign.teachers != current_user:
                abort(403)
    try:
        data = dict(request.form)
        # trying to update date
        if data.get('year_of_study'):
            data['year_of_study'] = int(data.get('year_of_study'))
        if data.get('due_date'):
            data['due_date'] = datetime.strptime(
                data.get('due_date'), BaseModel.DATE_FORMAT)
        updated = db_controller.update(Assignment, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@assignm_blueprint.route('/assignments/<int:id>', methods=['DELETE'], strict_slashes=False)
@jwt_required(optional=True)
def delete_assignment(id):
    """function for delete endpoint, it handles Assignment deletion"""
    user = current_user.__tablename__
    if user == 'students':
        return jsonify(ERROR='Admins only'), 403

    if user == 'teachers':
        assign = db_controller.get_by_id(Assignment, id)
        if assign.teachers:
            if assign.teachers != current_user:
                abort(403)
    try:
        db_controller.delete(Assignment, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted assignment"), 200


# helpers
def find_assignm_submissions(assignment):
    """Find department scores"""
    all_submissions = []
    subms = assignment.submissions
    for sub in subms:
        all_submissions.append(sub.to_dict())
    return all_submissions


def find_assingm_teachers(assignm):
    """find course that are associated with the department"""
    return assignm.teachers.to_dict()


def args_handler(assignment, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('submissions') == 'true':
        assignm_submissions = find_assignm_submissions(assignment)
        status_code = 200
        return {"assingment": assignment.assign_title,
                "submissions": assignm_submissions}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
