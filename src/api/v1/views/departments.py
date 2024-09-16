from flask_jwt_extended import jwt_required, current_user
from flask_login import current_user
from models.models import (
    Department, Material, MaterialDepartments,
    Admin, Student, Teacher
)
from api.v1.views import dept_blueprint
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from datetime import datetime

from flask_jwt_extended import current_user, jwt_required


BASE_URL = 'http://localhost:5000/api/v1'

# NEWLY ADDED


@dept_blueprint.route('/dept/<id>/courses', methods=['GET'], strict_slashes=False)
def dept_courses(id):
    dept = db_controller.get_by_id(Department, id)
    courses = dept.courses
    return jsonify(msg=f"yes-> {id}")


@dept_blueprint.route('/dept/<id>/courses/<yos>', methods=['GET'], strict_slashes=False)
def dept_courses_by_yos(id, yos):
    """
        Returns course for a certain year of study (yos) based on department id\n
        id: str Department id\n
        yos: str Year of Study
    """
    dept = db_controller.get_by_id(Department, id)
    courses = [course.to_dict()
               for course in dept.courses if course.year_of_study == int(yos)]
    return jsonify(msg="OK", courses=courses), 200


@dept_blueprint.route('/departments', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def departments():
    """returns all deparments objects from the db_controller"""
    new_obj = {}
    all_depts = []
    if current_user:
        if isinstance(current_user, Student):
            depts = [current_user.department]
        elif isinstance(current_user, Teacher):
            depts = current_user.departments
    else:
        depts = db_controller.get_all_object(Department)
    for dept in depts:
        courses = [course.to_dict()
                   for course in dept.courses if dept.courses]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in dept.materials if dept.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in dept.teachers if dept.teachers]
        students = [
            f'{BASE_URL}/students/{student.regno}'
            for student in dept.students if dept.students]
        communications = [
            f'{BASE_URL}/communications/{comm.id}'
            for comm in dept.communications if dept.communications]
        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in dept.submissions if dept.submissions]
        scores = [
            f'{BASE_URL}/scores/{score.id}'
            for score in dept.scores if dept.scores]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in departments.assignments] yet to be implemented

        for k, v in dept.to_dict().items():
            if k in ['dept_code', 'dept_name', 'duration', 'trimester_or_semester',
                     'n_teachers', 'hod', 'credits', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj["courses"] = courses
        all_depts.append(new_obj)
        new_obj = {}
    return jsonify({"departments": all_depts, "user_type": current_user.__class__.__name__ if current_user else None}), 200


@dept_blueprint.route('/departments/<code>', methods=['GET'], strict_slashes=False)
def one_department(code):
    """ endpoint that handle retrival of department by is code"""
    holder_old = {}
    new_obj = {}
    dept = db_controller.get_by_id(Department, code)
    if dept:
        courses = [
            f'{BASE_URL}/courses/{course.course_code}'
            for course in dept.courses if dept.courses]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in dept.materials if dept.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in dept.teachers if dept.teachers]
        students = [
            f'{BASE_URL}/students/{student.regno}'
            for student in dept.students if dept.students]
        communications = [
            f'{BASE_URL}/communications/{comm.id}'
            for comm in dept.communications if dept.communications]
        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in dept.submissions if dept.submissions]
        scores = [
            f'{BASE_URL}/scores/{score.id}'
            for score in dept.scores if dept.scores]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in departments.assignments] yet to be implemented

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(dept, args_dict)
            return jsonify([data]), status_code
        for k, v in dept.to_dict().items():
            if k in ['dept_code', 'dept_name', 'duration', 'trimester_or_semester',
                     'n_teachers', 'hod', 'credits', 'created_at', 'updated_at']:
                holder_old[k] = v
        holder_old['courses'] = courses
        holder_old['materials'] = materials
        holder_old['teachers'] = teachers
        holder_old['students'] = students
        holder_old['communications'] = communications
        holder_old['submissions'] = submissions
        holder_old['scores'] = scores

        if isinstance(current_user, Admin):
            new_obj = holder_old
        if isinstance(current_user, Teacher):
            if current_user in dept.teachers:
                new_obj = holder_old
        if isinstance(current_user, Student):
            if current_user.dept_id == dept.dept_code:
                new_obj = holder_old

        return jsonify({"department": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@dept_blueprint.route('/departments/', methods=['POST'], strict_slashes=False)
def create_department():
    """function that handles creation endpoint for Department instance"""
    data = dict(request.form)
    if not isinstance(current_user, Admin):
        abort(403)
    # check for hod
    if data['hod']:
        hod = db_controller.get_by_id(Teacher, data['hod'])
        if not hod:
            return jsonify(ERROR='Teacher not found'), 404
    try:
        # check if it exists
        find_dept = db_controller.get_by_id(Department, data['dept_code'])
        if find_dept:
            return jsonify(error="Department already exist")
        created = db_controller.create_object(Department(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "id": created.dept_name}), 201


@dept_blueprint.route('/departments/<code>', methods=['PUT'], strict_slashes=False)
def update_department(code):
    """ function that handles update endpoint for Department instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        data = dict(request.form)
        if data.get('duration'):
            data['duration'] = int(data.get('duration'))
        if data.get('credits'):
            data['credits'] = int(data.get('credits'))
        if data.get('n_teachers'):
            data['n_teachers'] = int(data.get('n_teachers'))

        updated = db_controller.update(Department, code, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.dept_code}), 201


@dept_blueprint.route('/departments/<code>', methods=['DELETE'], strict_slashes=False)
def delete_department(code):
    """function for delete endpoint, it handles course deletion"""

    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(Department, code)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted course"), 200


# DEPARTMENT AND MATERIALS ASSOCIATION ENDPOINTS
"""
@dept_blueprint.route('/dept_material', methods=['GET'], strict_slashes=False)
def dept_material():
    return all department and material associations
    new_obj = {}
    all_associations = []
    dept_mat_assoc = db_controller.get_all_object(MaterialDepartments)
    if dept_mat_assoc:
        for td in dept_mat_assoc:
            department = [
                td.department.to_dict() if td.department else None]
            material = [
                td.material.to_dict() if td.material else None]

            for k, v in td.to_dict().items():
                if k in ['id', 'date_uploaded',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['department'] = department
            new_obj['material'] = material
            all_associations.append(new_obj)
            new_obj = {}
        return jsonify({"department-materials associations": all_associations}), 200
    else:
        return jsonify(ERROR='Nothing found')


@dept_blueprint.route('/dept_material/<int:id>', methods=['GET'],
                      strict_slashes=False)
def single_dept_material(id):
    eturn a department-material association
    new_obj = {}
    td = db_controller.get_by_id(MaterialDepartments, id)
    if td:
        department = [
            td.department.to_dict() if td.department else None]
        material = [
            td.material.to_dict() if td.material else None]

        for k, v in td.to_dict().items():
            if k in ['id', 'date_uploaded',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['department'] = department
        new_obj['material'] = material
        return jsonify({"dept-material association": new_obj}), 200
    else:
        return jsonify(ERROR="Nothing found")

"""


@dept_blueprint.route('/dept_material', methods=['POST'], strict_slashes=False)
def create_dept_material_ass():
    """create a department-material association instance"""
    data = dict(request.form)
    if not isinstance(current_user, Admin):
        abort(403)
    # check material or department existence
    mat = db_controller.get_by_id(Material, int(data['material_id']))
    if not mat:
        return jsonify(ERROR='Material not found'), 404
    dept = db_controller.get_by_id(Department, data['department_id'])
    if not dept:
        return jsonify(ERROR='Department not found'), 404
    try:
        # check if it exists
        assoc = db_controller.search(MaterialDepartments, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        created = db_controller.create_object(MaterialDepartments(**data))
    except Exception as e:
        db_controller._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@dept_blueprint.route('/dept_material/<int:id>', methods=['PUT'], strict_slashes=False)
def update_dept_material(id):
    """update department-material association object"""
    data = dict(request.form)
    if not isinstance(current_user, Admin):
        abort(403)
    data['updated_at'] = datetime.utcnow()
    if data.get('material_id'):
        mat = db_controller.get_by_id(Material, data.get('material_id'))
        if not mat:
            return jsonify(ERROR='Materials not exists')
        data['material_id'] = int(data['material_id'])
    if data.get('department_id'):
        dept = db_controller.get_by_id(Department, data.get('department_id'))
        if not dept:
            return jsonify(ERROR='Department not found')

    try:
        updated = db_controller.update(MaterialDepartments, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@dept_blueprint.route('/dept_material/<int:id>', methods=['DELETE'], strict_slashes=False)
def remove_dept_crs(id):
    """remove association between department-material"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(MaterialDepartments, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200


# helpers
def find_dept_scores(dept):
    """Find department scores"""
    all_scores = []
    scores = dept.scores
    for score in scores:
        all_scores.append(score.to_dict())
    return all_scores


def find_dept_materials(dept):
    """find department materials"""
    all_materials = []
    materials = dept.materials
    for mat in materials:
        all_materials.append(mat.to_dict())
    return all_materials


def find_dept_courses(dept):
    """find course that are associated with the department"""
    all_courses = []
    courses = dept.courses
    for course in courses:
        all_courses.append(course.to_dict())
    return all_courses


def args_handler(dept, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('scores') == 'true':
        dept_scores = find_dept_scores(dept)
        status_code = 200
        return {"scores": {"department": dept.dept_code,
                           "score": dept_scores}}, status_code
    elif args.get('materials') == 'true':
        dept_materials = find_dept_materials(dept)
        status_code = 200
        return {"department": dept.dept_code,
                "materials": dept_materials}, status_code
    elif args.get('courses') == 'true':
        dept_courses = find_dept_courses(dept)
        status_code = 200
        return {f"{dept.dept_code} courses": dept_courses}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
