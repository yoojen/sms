from models.roles_and_admins import Role, Admin, RoleAdmin
from api.v1.views import roles_n_admin_bp
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound


BASE_URL = 'http://localhost:5000/api/v1'


@roles_n_admin_bp.route('/roles', methods=['GET'], strict_slashes=False)
def roles():
    """returns all Role objects from the db"""
    new_obj = {}
    all_roles = []
    roles = db.get_all_object(Role)
    for role in roles:
        admins = [
            f'{BASE_URL}/admins/{admin.id}'
            for admin in role.admins]
        for k, v in role.to_json().items():
            if k in ['id', 'role_name', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['admins'] = admins
        all_roles.append(new_obj)
        new_obj = {}
    return jsonify({"roles": all_roles}), 200


@roles_n_admin_bp.route('/roles/<int:id>', methods=['GET'],
                        strict_slashes=False)
def one_role(id):
    """returns single Role object from the db"""

    new_obj = {}
    role = db.get_by_id(Role, id)
    if role:
        admins = [
            f'{BASE_URL}/admins/{admin.id}'
            for admin in role.admins]
        for k, v in role.to_json().items():
            if k in ['id', 'role_name', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['admins'] = admins

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(role, args_dict)
            return jsonify(data), status_code
        return jsonify({"roles": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@roles_n_admin_bp.route('/roles/', methods=['POST'],
                        strict_slashes=False)
def create_role():
    """function that handles creation endpoint for Role instance"""
    data = dict(request.form)
    try:
        # check if it exists
        role = db.get_by_id(Role, data.get('id'))
        if role:
            return jsonify(error="Role already exist")
        created = db.create_object(Role(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "role": created.role_name}), 201


@roles_n_admin_bp.route('/roles/<int:id>', methods=['PUT'],
                        strict_slashes=False)
def update_department(id):
    """ function that handles update endpoint for Role instance"""
    try:
        data = dict(request.form)
        if len(data.get('role_name')) < 5:
            return jsonify(ERROR="role name must be atleast 5 characters")
        updated = db.update(Role, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@roles_n_admin_bp.route('/roles/<int:id>', methods=['DELETE'],
                        strict_slashes=False)
def delete_role(id):
    """function for delete endpoint, it handles Role deletion"""
    try:
        db.delete(Role, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted role"), 200


def find_admin_with_role(role):
    """finds all admins with this role"""
    all_admins = []
    admins = role.admins
    for admin in admins:
        all_admins.append(admin.to_json())
    return all_admins


def args_handler(role, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('admins') == 'true':
        admins = find_admin_with_role(role)
        status_code = 200
        return {"role": role.id,
                "admins": admins}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
