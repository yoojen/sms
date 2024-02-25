from models.courses_departments import Course
from models.materials_and_matdept import Material
from api.v1.views import material_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound

from models.teachers_and_degree import Teacher


BASE_URL = 'http://localhost:5000/api/v1'


@material_blueprint.route('/materials', methods=['GET'], strict_slashes=False)
def materials():
    """returns all Materials objects from the db"""

    new_obj = {}
    all_materials = []
    materials = db.get_all_object(Material)
    for material in materials:
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in material.departments]
        course = f'{BASE_URL}/courses/{ material.course.course_code}'

        teacher = f'{BASE_URL}/teachers/{material.teacher.id}'

        for k, v in material.to_json().items():
            if k in ['id', 'course_code', 'teacher_id', 'year_of_study',
                     'description', 'file_path', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['departments'] = departments
        new_obj['course'] = course
        new_obj['teacher'] = teacher
        all_materials.append(new_obj)
        new_obj = {}
    return jsonify({"materials": all_materials}), 200


@material_blueprint.route('/materials/<int:id>', methods=['GET'],
                          strict_slashes=False)
def single_materials(id):
    """returns single Material object from the db"""

    new_obj = {}
    material = db.get_by_id(Material, id)
    if material:
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in material.departments]
        course = f'{BASE_URL}/courses/{ material.course.course_code}'

        teacher = f'{BASE_URL}/teachers/{material.teacher.id}'

        for k, v in material.to_json().items():
            if k in ['id', 'course_code', 'teacher_id', 'year_of_study',
                     'description', 'file_path', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['departments'] = departments
        new_obj['course'] = course
        new_obj['teacher'] = teacher

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
def create_material():
    """function that handles creation endpoint for Material instance"""
    data = dict(request.form)
    # check teacher or course availability
    teacher = db.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    course = db.get_by_id(Course, data['course_code'])
    if not course:
        return jsonify(ERROR='Course does not exists'), 404
    try:
        # check if it exists
        find_dept = db.get_by_id(Material, data.get('id'))
        if find_dept:
            return jsonify(error="Material already exist"), 409
        created = db.create_object(Material(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "location": created.file_path}), 201


@material_blueprint.route('/materials/<int:id>', methods=['PUT'],
                          strict_slashes=False)
def update_department(id):
    """ function that handles update endpoint for Material instance"""
    try:
        data = dict(request.form)
        if data.get('year_of_study'):
            data['year_of_study'] = int(data.get('year_of_study'))
        updated = db.update(Material, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@material_blueprint.route('/materials/<int:id>', methods=['DELETE'],
                          strict_slashes=False)
def delete_material(id):
    """function for delete endpoint, it handles Material deletion"""

    try:
        db.delete(Material, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted material"), 200


# helpers
def find_material_depts(mat):
    """Find department associated with material"""
    all_depts = []
    depts = mat.departments
    for dept in depts:
        all_depts.append(dept.to_json())
    return all_depts


def find_material_teacher(mat):
    """find department materials"""
    return mat.teacher.to_json()


def find_material_course(mat):
    """find course that are associated with the material"""
    return mat.course.to_json()


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
