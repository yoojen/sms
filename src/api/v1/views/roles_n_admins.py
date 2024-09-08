from flask_login import current_user, login_required
from models.roles_and_admins import Role, Admin, RoleAdmin
from api.v1.views import roles_n_admin_bp
from api.engine import db
import bcrypt
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import date, datetime

BASE_URL = 'http://localhost:5000/api/v1'


@roles_n_admin_bp.route('/roles', methods=['GET'], strict_slashes=False)
@login_required
def roles():
    """returns all Role objects from the db"""
    if not isinstance(current_user, Admin):
        abort(403)
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
@login_required
def one_role(id):
    """returns single Role object from the db"""
    if not isinstance(current_user, Admin):
        abort(403)
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
@login_required
def create_role():
    """function that handles creation endpoint for Role instance"""
    data = dict(request.form)
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        # check if it exists
        role = db.search(Role, role_name=data.get('role_name'))
        if role:
            return jsonify(error="Role already exist"), 409
        created = db.create_object(Role(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "role": created.role_name}), 201


@roles_n_admin_bp.route('/roles/<int:id>', methods=['PUT'],
                        strict_slashes=False)
@login_required
def update_department(id):
    """ function that handles update endpoint for Role instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        data = dict(request.form)
        data['updated_at'] = datetime.utcnow()
        if len(data.get('role_name')) < 5:
            return jsonify(ERROR="role name must be atleast 5 characters"), 400
        updated = db.update(Role, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@roles_n_admin_bp.route('/roles/<int:id>', methods=['DELETE'],
                        strict_slashes=False)
@login_required
def delete_role(id):
    """function for delete endpoint, it handles Role deletion"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db.delete(Role, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 404
    return jsonify(message="Successfully deleted role"), 200


# admins endpoints
@roles_n_admin_bp.route('/admins', methods=['GET'], strict_slashes=False)
@login_required
def admins():
    """returns all Admin objects from the db"""
    if not isinstance(current_user, Admin):
        abort(403)
    new_obj = {}
    all_admins = []
    admins = db.get_all_object(Admin)
    for admin in admins:
        roles = [
            f'{BASE_URL}/roles/{role.id}'
            for role in admin.roles]
        course_created = [
            f'{BASE_URL}/courses/{course.course_code}'
            for course in admin.courses]
        for k, v in admin.to_json().items():
            if k in ['id', 'first_name', 'last_name', 'email', 'citizenship', 'tel',
                     'dob', 'last_login', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['roles'] = roles
        new_obj['course_created'] = course_created
        all_admins.append(new_obj)
        new_obj = {}
    return jsonify({"admins": all_admins}), 200


@roles_n_admin_bp.route('/admins/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def one_admin(id):
    """returns all Admin objects from the db"""
    if not isinstance(current_user, Admin):
        abort(403)
    new_obj = {}
    admin = db.get_by_id(Admin, id)
    if admin:
        roles = [
            f'{BASE_URL}/roles/{role.id}'
            for role in admin.roles]
        course_created = [
            f'{BASE_URL}/courses/{course.course_code}'
            for course in admin.courses]
        for k, v in admin.to_json().items():
            if k in ['id', 'first_name', 'last_name', 'email', 'citizenship', 'tel',
                     'dob', 'last_login', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['roles'] = roles
        new_obj['course_created'] = course_created

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            if args_dict.get('roles') == 'true':
                roles = [role.to_json() for role in admin.roles]
                return jsonify(roles=roles), 200
            elif args_dict.get('courses') == 'true':
                courses = [crs.to_json() for crs in admin.courses]
                return jsonify(courses=courses), 200
            else:
                return jsonify(ERROR='Not implemented'), 400
        return jsonify({"admins": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@roles_n_admin_bp.route('/admins/', methods=['POST'], strict_slashes=False)
@login_required
def create_admin():
    """function that handles creation endpoint for Admin instance"""
    admin_roles = [role.role_name for role in current_user.roles]
    if not 'super admin' in admin_roles:
        abort(403)
    data = dict(request.form)
    try:
        dob = data['dob'].split('-')
        password_bytes = data.get('password').encode()
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        data['password'] = hashed_password
        # check if it exists
        data['dob'] = date(int(dob[0]), int(dob[1]), int(dob[2]))
        admin = db.get_by_id(Admin, data.get('id'))
        if admin:
            return jsonify(error="Admin already exist"), 409
        created = db.create_object(Admin(**data))
    except Exception as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "role": created.email}), 201


@roles_n_admin_bp.route('/admins/<int:id>', methods=['PUT'],
                        strict_slashes=False)
@login_required
def update_admin(id):
    """ function that handles update endpoint for Admin instance"""
    admin_roles = [role.role_name for role in current_user.roles]
    if not 'super admin' in admin_roles:
        abort(403)
    try:
        data = dict(request.form)
        if data.get('dob'):
            data['dob'] = datetime.strptime(data.get('dob'),
                                            BaseModel.DATE_FORMAT)

        updated = db.update(Admin, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.email}), 201


@roles_n_admin_bp.route('/admins/<int:id>', methods=['DELETE'],
                        strict_slashes=False)
@login_required
def delete_admin(id):
    """function for delete endpoint, it handles Admin deletion"""
    admin_roles = [role.role_name for role in current_user.roles]
    if not 'super admin' in admin_roles:
        abort(403)
    try:
        db.delete(Admin, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 404
    return jsonify(message="Successfully deleted admin"), 204


# role_admin endnpoints
@roles_n_admin_bp.route('/admin_role', methods=['POST'], strict_slashes=False)
@login_required
def create_adminrole():
    """create association between admin and roles"""
    admin_roles = [role.role_name for role in current_user.roles]
    if not 'super admin' in admin_roles:
        abort(403)
    data = dict(request.form)
    admin = db.get_by_id(Admin, data['admin_id'])
    if not admin:
        return jsonify(ERROR='Admin not exists'), 404
    role = db.get_by_id(Role, data['role_id'])
    if not role:
        return jsonify(ERROR='Role not found')

    ad_roles = db.search(RoleAdmin, admin_id=int(data.get(
        'admin_id')), role_id=int(data.get('role_id')))
    if ad_roles:
        return jsonify(ERROR='Association exists'), 409
    try:
        created = db.create_object(RoleAdmin(**data))
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Created successfully", "id": created.id}), 201


@roles_n_admin_bp.route('/admin_role/<int:id>', methods=['PUT', 'DELETE'], strict_slashes=False)
def put_delete_adminrole(id):
    """handles update and delete of admin_role association"""
    admin_roles = [role.role_name for role in current_user.roles]
    if not 'super admin' in admin_roles:
        abort(403)
    admin_role = db.get_by_id(RoleAdmin, id)
    data = dict(request.form)
    if admin_role:
        if request.method == 'PUT':
            try:
                updated = db.update(RoleAdmin, id, **data)
            except Exception as error:
                return jsonify(ERROR=str(error)), 400
            return jsonify({"message": "Successfully updated",
                            "id": updated.id}), 201
        if request.method == 'DELETE':
            try:
                db.delete(RoleAdmin, id)
            except NoResultFound as e:
                return jsonify(ERROR=str(e)), 404
            return jsonify(message="Successfully deleted association"), 200
    return jsonify(ERROR='Not found'), 404


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
