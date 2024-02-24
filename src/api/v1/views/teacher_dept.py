from models.teacher_dept import TeacherDepartments
from api.v1.views import teacher_bp
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'


@teacher_bp.route('/teacher_dept', methods=['GET'], strict_slashes=False)
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
def create_teacher_association():
    """create a teacher degree association instance"""
    data = dict(request.form)
    if data.get('date_assigned'):
        data['date_assigned'] = datetime.strptime(
            data['date_assigned'], BaseModel.DATE_FORMAT)
    try:
        # check if it exists
        # CHECK IF TEACHER AND DEPARTMENT IDS ALREDY ARE THERE
        created = db.create_object(TeacherDepartments(**data))
    except Exception as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@teacher_bp.route('/teacher_dept/<int:id>', methods=['PUT'], strict_slashes=False)
def update_association_object(id):
    """update teacher degree association object"""
    data = dict(request.form)
    if data.get('teacher_id'):
        data['teacher_id'] = int(data['teacher_id'])
    try:
        # NORMALLY, CHECK ROW WITH TEACHER AND DEGREE ID
        # IF FOUND UPDATE ANY COLUMN
        updated = db.update(TeacherDepartments, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@teacher_bp.route('/teacher_dept/<int:id>', methods=['DELETE'], strict_slashes=False)
def remove_association(id):
    """remove association between degree and teacher"""

    try:
        db.delete(TeacherDepartments, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200
