from models.assignments import Assignment
from api.v1.views import assignm_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime


BASE_URL = 'http://localhost:5000/api/v1'


@assignm_blueprint.route('/assignments', methods=['GET'], strict_slashes=False)
def assignments():
    """returns all Assignments objects from the db"""

    new_obj = {}
    all_assignms = []
    assignms = db.get_all_object(Assignment)
    for assignm in assignms:
        # courses = [
        #     f'{BASE_URL}/courses/{course.course_code}'
        #     for course in assignm.course] -- NOT YET IMPLEMENTED

        teacher = f'{BASE_URL}/teachers/{assignm.teachers.id}'

        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in assignm.submissions]

        for k, v in assignm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                     'year_of_study', 'due_date', 'description', 'file_path',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['submissions'] = submissions
        all_assignms.append(new_obj)
        new_obj = {}
    return jsonify({"assignments": all_assignms}), 200


@assignm_blueprint.route('/assignments/<int:id>', methods=['GET'], strict_slashes=False)
def one_assignment(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    assignm = db.get_by_id(Assignment, id)
    if assignm:
        teacher = f'{BASE_URL}/teachers/{assignm.teachers.id}'

        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in assignm.submissions]

        for k, v in assignm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                     'year_of_study', 'due_date', 'description', 'file_path',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['submissions'] = submissions
        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(assignm, args_dict)
            return jsonify([data]), status_code
        return jsonify({"assignment": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@assignm_blueprint.route('/assignments/', methods=['POST'], strict_slashes=False)
def create_assignments():
    """function that handles creation endpoint for Assignment instance"""
    data = dict(request.form)
    data['due_date'] = datetime.strptime(
        data.get('due_date'), BaseModel.DATE_FORMAT)
    try:
        # check if it exists
        find_dept = db.get_by_id(Assignment, data.get('id'))
        if find_dept:
            return jsonify(error="Assignment already exist")
        created = db.create_object(Assignment(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "title": created.assign_title}), 201


@assignm_blueprint.route('/assignments/<int:id>', methods=['PUT'], strict_slashes=False)
def update_assignment(id):
    """ function that handles update endpoint for Assignment instance"""
    try:
        data = dict(request.form)
        # trying to update date
        if data.get('year_of_study'):
            data['year_of_study'] = int(data.get('year_of_study'))
        if data.get('due_date'):
            data['due_date'] = datetime.strptime(
                data.get('due_date'), BaseModel.DATE_FORMAT)
        updated = db.update(Assignment, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@assignm_blueprint.route('/assignments/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_assignment(id):
    """function for delete endpoint, it handles Assignment deletion"""

    try:
        db.delete(Assignment, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted assignment"), 200


# helpers
def find_assignm_submissions(assignment):
    """Find department scores"""
    all_submissions = []
    subms = assignment.submissions
    for sub in subms:
        all_submissions.append(sub.to_json())
    return all_submissions


def find_assingm_teachers(assignm):
    """find course that are associated with the department"""
    return assignm.teachers.to_json()


def args_handler(assignment, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('submissions') == 'true':
        assignm_submissions = find_assignm_submissions(assignment)
        status_code = 200
        return jsonify({"assingment": assignment.assign_title,
                        "submissions": assignm_submissions}), status_code
    elif args.get('teachers') == 'true':
        assig_teacher = find_assingm_teachers(assignment)
        status_code = 200
        return {f"{assignment.assign_title} teacher": assig_teacher}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
