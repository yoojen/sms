from flask_login import current_user, login_required
from models.roles_and_admins import Admin
from models.students import Student
from models.teachers_and_degree import (Degree,
                                        TeacherDegree, Teacher)
from api.v1.views import degree_bp
from api.engine import db
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound


BASE_URL = 'http://localhost:5000/api/v1'


@degree_bp.route('/degrees', methods=['GET'], strict_slashes=False)
@login_required
def get_degrees():
    """return all Degree instance from the storage"""
    new_obj = {}
    all_degrees = []
    if isinstance(current_user, Student):
        abort(404)
    degrees = db.get_all_object(Degree)
    if degrees:
        for degree in degrees:
            teachers = [f'{BASE_URL}/teachers/{teacher.id }'
                        for teacher in degree.teachers]

            for k, v in degree.to_json().items():
                if k in ['id', 'degree_name', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['teachers'] = teachers
            if isinstance(current_user, Admin):
                all_degrees.append(new_obj)

            if isinstance(current_user, Teacher):
                if current_user in degree.teachers:
                    all_degrees.append(new_obj)
            new_obj = {}
        return jsonify({"degrees": all_degrees}), 200
    return jsonify(MESSAGE="Nothing found"), 200


@degree_bp.route('/degrees/<int:id>', methods=['GET'],
                 strict_slashes=False)
@login_required
def single_degree(id):
    """return single Degree instance from the storage"""
    new_obj = {}
    if isinstance(current_user, Student):
        abort(404)
    degree = db.get_by_id(Degree, id)
    if degree:
        if isinstance(current_user, Admin):
            teachers = [f'{BASE_URL}/teachers/{teacher.id }'
                        for teacher in degree.teachers]
            for k, v in degree.to_json().items():
                if k in ['id', 'degree_name', 'created_at', 'updated_at']:
                    new_obj[k] = v
                    new_obj['teachers'] = teachers
        if isinstance(current_user, Teacher):
            if degree in current_user.degrees:
                for k, v in degree.to_json().items():
                    if k in ['id', 'degree_name', 'created_at', 'updated_at']:
                        new_obj[k] = v
        return jsonify({"degrees": new_obj}), 200
    return jsonify(message="Nothing found"), 200


@degree_bp.route('/degrees', methods=['POST'],
                 strict_slashes=False)
@login_required
def create_degree():
    """function that handles creation endpoint for Degree instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    find_dg = db.search(Degree, degree_name=data.get('degree_name'))
    if find_dg:
        return jsonify(ERROR='Alredy exists'), 409
    try:
        # check if it exists
        created = db.create_object(Degree(**data))
    except ValueError as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "email": created.degree_name}), 201


@degree_bp.route('/degrees/<int:id>', methods=['PUT'],
                 strict_slashes=False)
@login_required
def update_degree(id):
    """ function that handles update endpoint for Degree instance"""
    if current_user.__tablename__ != 'admins':
        abort(403)
    data = dict(request.form)
    try:
        updated = db.update(Degree, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.degree_name}), 201


@degree_bp.route('/degrees/<int:id>', methods=['DELETE'],
                 strict_slashes=False)
@login_required
def delete_degree(id):
    """function for delete endpoint, it handles Degree deletion"""
    if current_user.__tablename__ == 'students':
        abort(403)
    try:
        db.delete(Degree, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted a degree"), 200


# teacher_degree association endpoints
@degree_bp.route('/teacher_degree', methods=['GET'], strict_slashes=False)
@login_required
def teacher_degree():
    """return all teacher and degree associations"""
    new_obj = {}
    all_associations = []
    tchr_degree_associationss = db.get_all_object(TeacherDegree)
    if tchr_degree_associationss:
        for td in tchr_degree_associationss:
            teachers = [
                td.teacher.to_json() if td.teacher else None]
            degrees = [
                td.degree.to_json() if td.degree else None]

            for k, v in td.to_json().items():
                if k in ['id', 'teacher_id', 'degree_id',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['teachers'] = teachers
            new_obj['degrees'] = degrees
            all_associations.append(new_obj)
            new_obj = {}
        return jsonify({"teacher degree associations": all_associations}), 200
    else:
        return jsonify(ERROR='Nothing found'), 404


@degree_bp.route('/teacher_degree/<int:id>', methods=['GET'],
                 strict_slashes=False)
@login_required
def single_teacher_degree(id):
    """return a teacher degree association based on teacher id"""
    new_obj = {}
    td = db.get_by_id(TeacherDegree, id)
    if td:
        teachers = [
            td.teacher.to_json() if td.teacher else None]
        degrees = [
            td.degree.to_json() if td.degree else None]

        for k, v in td.to_json().items():
            if k in ['id', 'teacher_id', 'degree_id',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teachers'] = teachers
        new_obj['degrees'] = degrees
        return jsonify({"td association": new_obj})
    else:
        return jsonify(ERROR="Nothing found")


@degree_bp.route('/teacher_degree', methods=['POST'], strict_slashes=False)
@login_required
def create_teacherdegree_association():
    """create a teacher degree association instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    data['teacher_id'] = int(data.get('teacher_id'))
    # check if degree or teacher exists in db
    teacher = db.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    degree = db.get_by_id(Degree, int(data['degree_id']))
    if not degree:
        return jsonify(ERROR='Degree does not exists'), 404
    try:
        # check if it exists
        assoc = db.search(TeacherDegree, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        created = db.create_object(TeacherDegree(**data))
    except Exception as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@degree_bp.route('/teacher_degree/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_association_object(id):
    """update teacher degree association object"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    if data.get('teacher_id'):
        data['teacher_id'] = int(data['teacher_id'])
        teacher = db.get_by_id(Teacher, data['teacher_id'])
        if not teacher:
            return jsonify(ERROR='Teacher does not exists'), 404
    if data.get('degree_id'):
        data['degree_id'] = int(data['degree_id'])
        degree = db.get_by_id(Degree, int(data['degree_id']))
        if not degree:
            return jsonify(ERROR='Degree does not exists'), 404
    try:
        updated = db.update(TeacherDegree, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@degree_bp.route('/teacher_degree/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_association(id):
    """remove association between degree and teacher"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db.delete(TeacherDegree, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200
