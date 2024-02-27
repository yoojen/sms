import json
from flask_login import current_user, login_required
from models.assignments import Assignment
from api.v1.views import assignm_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound, IntegrityError
from models.base_model import BaseModel
from datetime import datetime


BASE_URL = 'http://localhost:5000/api/v1'


@assignm_blueprint.route('/assignments', methods=['GET'], strict_slashes=False)
@login_required
def assignments():
    """returns all Assignments objects from the db"""
    new_obj = {}
    all_assignms = []
    assignms = db.get_all_object(Assignment)
    for assignm in assignms:
        if current_user.__tablename__ != 'students':
            ass_tchr = current_user.assignments
        ass_dept = assignm.department
        course = assignm.course.to_json()
        teacher = assignm.teachers.to_json()

        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in assignm.submissions]

        for k, v in assignm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                     'year_of_study', 'due_date', 'description', 'link',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        teacher['password'] = '***'
        new_obj['teacher'] = teacher
        new_obj['submissions'] = submissions
        new_obj['course'] = course
        if current_user.__tablename__ == 'students':
            if current_user.department:
                if ass_dept == current_user.department and \
                        assignm.year_of_study == current_user.year_of_study:
                    all_assignms.append(new_obj)
        if current_user.__tablename__ == 'admins':
            all_assignms.append(new_obj)
        if current_user.__tablename__ == 'teachers':
            tch_ass = current_user.assignments
            for ass in tch_ass:
                prsd = ass.to_json()
                prsd['course'] = prsd['course'].to_json()
                prsd['department'] = prsd['department'].to_json()
                del prsd['submissions']
                del prsd['teachers']
                all_assignms.append(prsd)
    return jsonify({"assignments": all_assignms}), 200


@assignm_blueprint.route('/assignments/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def one_assignment(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    assignm = db.get_by_id(Assignment, id)
    if assignm:
        ass_dept = assignm.department
        course = assignm.course.to_json()

        teacher = f'{BASE_URL}/teachers/{assignm.teachers.id}'

        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in assignm.submissions]

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(assignm, args_dict)
            return jsonify(data), status_code

        if current_user.__tablename__ == 'admins':
            """display course based on admin credentials"""
            for k, v in assignm.to_json().items():
                if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                         'year_of_study', 'due_date', 'description', 'link',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['teacher'] = teacher
            new_obj['course'] = course
            new_obj['submissions'] = submissions
        if current_user.__tablename__ == 'teachers':
            if current_user.assignments:
                if assignm in current_user.assignments:
                    for k, v in assignm.to_json().items():
                        if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                                 'year_of_study', 'due_date', 'description', 'link',
                                 'created_at', 'updated_at']:
                            new_obj[k] = v
                    new_obj['course'] = course
                    new_obj['teacher'] = teacher
                    new_obj['submissions'] = submissions

        if current_user.__tablename__ == 'students':
            if current_user.department:
                if current_user.department == ass_dept and\
                        assignm.year_of_study == current_user.year_of_study:
                    for k, v in assignm.to_json().items():
                        if k in ['id', 'teacher_id', 'dept_id', 'course_id', 'assign_title',
                                 'year_of_study', 'due_date', 'description', 'link',
                                 'created_at', 'updated_at']:
                            new_obj[k] = v
                    new_obj['course'] = course
                    new_obj['teacher'] = teacher
                    new_obj['submissions'] = submissions

        return jsonify({"assignment": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 200


@assignm_blueprint.route('/assignments/', methods=['POST'], strict_slashes=False)
@login_required
def create_assignments():
    """function that handles creation endpoint for Assignment instance"""
    user = current_user.__tablename__
    data = dict(request.form)
    data['due_date'] = datetime.strptime(
        data.get('due_date'), BaseModel.DATE_FORMAT)

    # Check if teacher, department or course really exist
    from models.teachers_and_degree import Teacher
    from models.courses_departments import Department
    from models.courses_departments import Course
    teacher = db.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db.get_by_id(Department, data['dept_id'])
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404
    course = db.get_by_id(Course, data['course_id'])
    if not course:
        return jsonify(ERROR='Course does not exists'), 404
    if user == 'admins' or user == 'teachers':
        try:
            # check if it exists
            find_dept = db.get_by_id(Assignment, data.get('id'))
            if find_dept:
                return jsonify(error="Assignment already exist")
            created = db.create_object(Assignment(**data))
        except Exception as e:
            return jsonify({"message": "Not created", "error": str(e)}), 400
        return jsonify({"message": "Successfully created",
                        "title": created.assign_title}), 201
    return jsonify(ERROR='Admins only')


@assignm_blueprint.route('/assignments/<int:id>', methods=['PUT'], strict_slashes=False)
def update_assignment(id):
    """ function that handles update endpoint for Assignment instance"""
    user = current_user.__tablename__

    if user == 'admins' or user == 'teachers':
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
    return jsonify(ERROR='Admins only')


@assignm_blueprint.route('/assignments/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_assignment(id):
    """function for delete endpoint, it handles Assignment deletion"""
    user = current_user.__tablename__

    if user == 'admins' or user == 'teachers':
        try:
            db.delete(Assignment, id)
        except NoResultFound as e:
            return jsonify(ERROR=str(e)), 400
        return jsonify(message="Successfully deleted assignment"), 200
    return jsonify(ERROR='Admins only')


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
        return {"assingment": assignment.assign_title,
                "submissions": assignm_submissions}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
