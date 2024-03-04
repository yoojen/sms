from flask_login import current_user, login_required
from models.courses_departments import Department
from models.roles_and_admins import Admin
from models.teacher_dept import TeacherDepartments
from api.v1.views import teacher_bp
from api.engine import db
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime

from models.teachers_and_degree import Teacher

BASE_URL = 'http://localhost:5000/api/v1'


@teacher_bp.route('/teacher_dept', methods=['GET'], strict_slashes=False)
@login_required
def teacher_dept():
    """return all teacher and department associations"""
    new_obj = {}
    all_associations = []
    tchr_dept_associations = db.get_all_object(TeacherDepartments)
    if tchr_dept_associations:
        for td in tchr_dept_associations:
            teacher = [
                td.teacher.to_json() if td.teacher else None]
            department = [
                td.department.to_json() if td.department else None]

            for k, v in td.to_json().items():
                if k in ['id', 'teacher_id', 'dept_id', 'date_assigned',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['teacher'] = teacher
            new_obj['department'] = department
            all_associations.append(new_obj)
            new_obj = {}
        return jsonify({"teacher department associations": all_associations}), 200
    else:
        return jsonify(ERROR='Nothing found'), 404


@teacher_bp.route('/teacher_dept/<int:id>', methods=['GET'],
                  strict_slashes=False)
@login_required
def single_teacher_dept(id):
    """return a teacher degree association based on teacher id"""
    new_obj = {}
    td = db.get_by_id(TeacherDepartments, id)
    if td:
        teacher = [
            td.teacher.to_json() if td.teacher else None]
        department = [
            td.department.to_json() if td.department else None]

        for k, v in td.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'date_assigned',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['department'] = department
        return jsonify({"td association": new_obj}), 200
    else:
        return jsonify(ERROR="Nothing found")


@teacher_bp.route('/teacher_dept', methods=['POST'], strict_slashes=False)
@login_required
def create_teacher_association():
    """create a teacher degree association instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)

    teacher = db.get_by_id(Teacher, int(data['teacher_id']))
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db.get_by_id(Department, data['dept_id'])
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404

    if data.get('date_assigned'):
        data['date_assigned'] = datetime.strptime(
            data['date_assigned'], BaseModel.DATE_FORMAT)
    data['teacher_id'] = int(data.get('teacher_id'))
    try:
        # check if it exists
        assoc = db.search(TeacherDepartments, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        created = db.create_object(TeacherDepartments(**data))
    except Exception as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@teacher_bp.route('/teacher_dept/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_association_object(id):
    """update teacher degree association object"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)

    teacher = db.get_by_id(Teacher, int(data['teacher_id']))
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db.get_by_id(Department, data['dept_id'])
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404

    data['teacher_id'] = int(data.get('teacher_id'))
    try:
        assoc = db.search(TeacherDepartments, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        updated = db.update(TeacherDepartments, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@teacher_bp.route('/teacher_dept/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_association(id):
    """remove association between degree and teacher"""
    if not isinstance(current_user, Admin):
        abort(403)

    try:
        db.delete(TeacherDepartments, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200
