from models.teachers_and_degree import Degree
from api.v1.views import degree_bp
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'


@degree_bp.route('/degrees', methods=['GET'], strict_slashes=False)
def get_degrees():
    """return all Degree instance from the storage"""
    new_obj = {}
    all_degrees = []
    degrees = db.get_all_object(Degree)
    if degrees:
        for degree in degrees:
            teachers = [f'{BASE_URL}/teachers/{teacher.id }'
                        for teacher in degree.teachers]

            for k, v in degree.to_json().items():
                if k in ['id', 'degree_name', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['teachers'] = teachers

            all_degrees.append(new_obj)
            new_obj = {}
        return jsonify({"degrees": all_degrees}), 200
    return jsonify(message="Nothing found"), 404


@degree_bp.route('/degrees/<int:id>', methods=['GET'],
                 strict_slashes=False)
def single_degree(id):
    """return single Degree instance from the storage"""
    new_obj = {}
    degree = db.get_by_id(Degree, id)
    if degree:
        teachers = [f'{BASE_URL}/teachers/{teacher.id }'
                    for teacher in degree.teachers]

        for k, v in degree.to_json().items():
            if k in ['id', 'degree_name', 'created_at', 'updated_at']:
                new_obj[k] = v

        new_obj['teachers'] = teachers
        return jsonify({"degrees": new_obj}), 200
    return jsonify(message="Nothing found"), 404


@degree_bp.route('/degrees', methods=['POST'],
                 strict_slashes=False)
def create_degree():
    """function that handles creation endpoint for Degree instance"""
    data = dict(request.form)
    try:
        # check if it exists
        created = db.create_object(Degree(**data))
    except Exception as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "email": created.degree_name}), 201


@degree_bp.route('/degrees/<int:id>', methods=['PUT'],
                 strict_slashes=False)
def update_degree(id):
    """ function that handles update endpoint for Degree instance"""
    data = dict(request.form)

    try:
        updated = db.update(Degree, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.degree_name}), 201


@degree_bp.route('/degrees/<int:id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_degree(id):
    """function for delete endpoint, it handles Degree deletion"""

    try:
        db.delete(Degree, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted a degree"), 200
