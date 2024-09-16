from api.v1.views import material_blueprint

from datetime import datetime
from flask_login import login_required
from models.models import (
    Course, Department, Material, Admin, Student, Teacher
    )
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from flask_jwt_extended import current_user, jwt_required


BASE_URL = 'http://localhost:5000/api/v1'

@material_blueprint.route('/materials', methods=['GET'], strict_slashes=False)
@jwt_required()
def materials():
    """returns all Materials objects from the db_controller"""

    new_obj = {}
    all_materials = []
    # if isinstance(current_user, )
    # materials = 
    materials = db_controller.get_all_object(Material)
    for material in materials:
        # print(dir(material))
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in material.departments]
        course = f'{BASE_URL}/courses/{ material.course.course_code}'

        teacher = f'{BASE_URL}/teachers/{material.teacher.id}' if material.teacher else None

        for k, v in material.to_dict().items():
            if k in ['id', 'course_code', 'teacher_id', 'year_of_study',
                     'description', 'link', 'created_at', 'updated_at']:
                new_obj[k] = v
        depts = material.departments
        depts_code = [dept.to_dict()["dept_code"] for dept in depts]
        new_obj['departments'] = [dept.to_dict() for dept in material.departments]
        new_obj['course'] = course
        new_obj['teacher'] = teacher

        if isinstance(current_user, Admin):
            all_materials.append(new_obj)
        if isinstance(current_user, Teacher):
            if material.teacher == current_user or \
                    set(material.departments) & set(current_user.departments):
                all_materials.append(new_obj)
        if current_user.year_of_study == material.year_of_study and \
            current_user.dept_id in depts_code:
                all_materials.append(new_obj)
        new_obj = {}
    return jsonify({"materials": all_materials, "user_type": current_user.__class__.__name__}), 200


@material_blueprint.route('/materials/<int:id>', methods=['GET'],
                          strict_slashes=False)
@login_required
def single_materials(id):
    """returns single Material object from the db_controller"""
    holder_old = {}
    new_obj = {}
    material = db_controller.get_by_id(Material, id)
    if material:
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in material.departments]
        course = f'{BASE_URL}/courses/{ material.course.course_code}'

        teacher = f'{BASE_URL}/teachers/{material.teacher.id}'

        for k, v in material.to_dict().items():
            if k in ['id', 'course_code', 'teacher_id', 'year_of_study',
                     'description', 'link', 'created_at', 'updated_at']:
                holder_old[k] = v
        holder_old['departments'] = departments
        holder_old['course'] = course
        holder_old['teacher'] = teacher
        if isinstance(current_user, Admin):
            new_obj = holder_old
        if isinstance(current_user, Teacher):
            if material.teacher == current_user or \
                    set(material.departments) & set(current_user.departments):
                new_obj = holder_old
        if isinstance(current_user, Student):
            if current_user.department in material.departments\
                    and current_user.year_of_study == material.year_of_study:
                new_obj = holder_old
        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(material, args_dict)
            return jsonify([data]), status_code

        return jsonify({"materials": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@material_blueprint.route('/materials/', methods=['POST'],
                          strict_slashes=False)
@login_required
def create_material():
    """function that handles creation endpoint for Material instance"""
    data = dict(request.form)
    if isinstance(current_user, Student):
        abort(403)
    # check teacher or course availability
    teacher = db_controller.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    course = db_controller.get_by_id(Course, data['course_code'])
    if not course:
        return jsonify(ERROR='Course does not exists'), 404

    try:
        # check if it exists
        find_dept = db_controller.get_by_id(Material, data.get('id'))
        if find_dept:
            return jsonify(error="Material already exist"), 409
        created = db_controller.create_object(Material(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "location": created.link}), 201


@material_blueprint.route('/materials/<int:id>', methods=['PUT'],
                          strict_slashes=False)
@login_required
def update_department(id):
    """ function that handles update endpoint for Material instance"""
    if isinstance(current_user, Student):
        abort(403)
    if isinstance(current_user, Teacher):
        mat = db_controller.get_by_id(Material, id)
        if int(mat.teacher_id) != int(current_user.id):
            abort(403)
    try:
        data = dict(request.form)
        data['updated_at'] = datetime.utcnow()
        if data.get('year_of_study'):
            data['year_of_study'] = int(data.get('year_of_study'))
        updated = db_controller.update(Material, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@material_blueprint.route('/materials/<int:id>', methods=['DELETE'],
                          strict_slashes=False)
@login_required
def delete_material(id):
    """function for delete endpoint, it handles Material deletion"""

    if isinstance(current_user, Student):
        abort(403)
    if isinstance(current_user, Teacher):
        mat = db_controller.get_by_id(Material, id)
        if int(mat.teacher_id) != int(current_user.id):
            abort(403)
    try:
        db_controller.delete(Material, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted material"), 200


# helpers
def find_material_depts(mat):
    """Find department associated with material"""
    all_depts = []
    depts = mat.departments
    for dept in depts:
        all_depts.append(dept.to_dict())
    return all_depts


def find_material_teacher(mat):
    """find department materials"""
    return mat.teacher.to_dict()


def find_material_course(mat):
    """find course that are associated with the material"""
    return mat.course.to_dict()


def args_handler(material, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('departments') == 'true':
        depts = find_material_depts(material)
        status_code = 200
        return {"materials": material.id,
                "departments": depts}, status_code
    elif args.get('teacher') == 'true':
        tchr = find_material_teacher(material)
        status_code = 200
        return {"material": material.id,
                "teacher": tchr}, status_code
    elif args.get('course') == 'true':
        mat_crs = find_material_course(material)
        status_code = 200
        return {f"materials <{material.id}>":
                {"courses": mat_crs}}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
