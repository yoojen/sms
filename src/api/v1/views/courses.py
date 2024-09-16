from models.models import (
    Course, Admin, Student, Teacher
)
from api.v1.views import course_blueprint
from api.engine import db_controller
from flask import abort, flash, jsonify, request
from datetime import date
from sqlalchemy.exc import NoResultFound
from flask_login import login_required
from flask_jwt_extended import current_user, jwt_required

BASE_URL = 'http://localhost:5000/api/v1'

# NWELY ADDED ENDPOINTS


@course_blueprint.route('/course/<code>/materials', methods=['GET'], strict_slashes=False)
def course_materials(code):
    course = db_controller.get_by_id(Course, code)
    if course:
        course_materials = [material.to_dict()
                            for material in course.materials]
        return jsonify(msg="OK", materials=course_materials), 200
    else:
        return jsonify(error="Not found"), 404


@course_blueprint.route('/courses', methods=['GET'], strict_slashes=False)
@jwt_required()
def courses():
    """returns all courses objects from the db"""
    new_obj = {}
    all_courses = []
    if isinstance(current_user, Admin):
        courses = db_controller.get_all_object(Course)
    elif isinstance(current_user, Student):
        courses = current_user.department.courses
        yos = current_user.year_of_study
    else:
        courses = None
    try:
        for course in courses:
            if yos and course.year_of_study == current_user.year_of_study:
                all_courses.append(course.to_dict())
    except:
        return jsonify(error="Nothing found")
    return jsonify({"courses": all_courses}), 200


@course_blueprint.route('/courses/<code>', methods=['GET'], strict_slashes=False)
@login_required
def courses_by_code(code):
    """endpoint that handle retrival of course by is code"""
    holder_obj = {}
    new_obj = {}
    course = db_controller.get_by_id(Course, code)
    if course:
        departments = [
            f'{BASE_URL}/departments/{depts.dept_code}'
            for depts in course.departments if course.departments]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in course.materials if course.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in course.teachers if course.teachers]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in course.assignments] yet to be implemented
        creator = f'{BASE_URL}/admins/{course.creator.id}' if course.creator else None

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            if len(args_dict) > 1:
                return jsonify(message="Not implemented")
            if args_dict.get('score') == 'true':
                course_scores = find_course_scores(code)
                return jsonify({"scores": {"course": course.course_code,
                                           "score": course_scores}}), 200
            elif args_dict.get('departments') == 'true':
                dept_with_crs = find_department_with_course(code)
                return jsonify({"departments": {"course": course.course_code,
                                                "departments": dept_with_crs}}), 200
            elif args_dict.get('materials') == 'true':
                crs_materials = find_crs_materials(code)
                return jsonify({"materials": {"course": course.course_code,
                                              "materials": crs_materials}}), 200
            else:
                return jsonify(message="Not implemented"), 400

        for k, v in course.to_dict().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                holder_obj[k] = v
        holder_obj['teachers'] = teachers
        holder_obj['departments'] = departments
        holder_obj['materials'] = materials
        holder_obj['creator'] = creator

        if current_user.__tablename__ == 'admins':
            """display course based on admin credentials"""
            new_obj = holder_obj
        if current_user.__tablename__ == 'teachers':
            for tc in course.teachers:
                if tc == current_user:
                    new_obj = holder_obj
        if current_user.__tablename__ == 'students':
            if current_user.department:
                if current_user.department in course.departments and\
                        course.year_of_study == current_user.year_of_study:
                    new_obj = holder_obj
    return jsonify({"course": new_obj}), 200


@course_blueprint.route('/courses/', methods=['POST'], strict_slashes=False)
@login_required
def create_course():
    """function that handles creation endpoint for Course instance"""
    data = dict(request.form)
    user = current_user.__tablename__

    if user != 'admins':
        abort(403)
    # check creator existence
    admin = db_controller.get_by_id(Admin, data['created_by'])
    if not admin:
        return jsonify(ERROR='Admin not exists')
    data['created_by'] = int(current_user.id)
    start_date = data['start_date'].split('-')
    end_date = data['end_date'].split('-')

    try:
        data['start_date'] = date(int(start_date[0]), int(
            start_date[1]), int(start_date[2]))
        data['end_date'] = date(int(end_date[0]), int(
            end_date[1]), int(end_date[2]))
        # check if it exists
        find_couse = db_controller.get_by_id(Course, data['course_code'])
        if find_couse:
            return jsonify(error="Course already exist")
        created = db_controller.create_object(Course(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    flash("created successfully")
    return jsonify({"message": "Successfully updated",
                    "id": created.course_name}), 201


@course_blueprint.route('/courses/<code>', methods=['PUT'], strict_slashes=False)
@login_required
def update_course(code):
    """function that handles update endpoint for Course instance"""

    if current_user.__tablename__ == 'admins':
        for role in current_user.roles:
            if not (role.role_name == 'super admin') or (role.role_name == 'editor'):
                return jsonify(ERROR="Admin only"), 403
        try:
            course = db_controller.get_by_id(Course, code)
            if course:
                data = dict(request.form)
                if data.get('start_date'):
                    start_date = data['start_date'].split('-')
                    data['start_date'] = date(int(start_date[0]), int(
                        start_date[1]), int(start_date[2]))
                if data.get('end_date'):
                    end_date = data['end_date'].split('-')
                    data['end_date'] = date(int(end_date[0]), int(
                        end_date[1]), int(end_date[2]))

                updated = db_controller.update(Course, code, **data)
                return jsonify({"message": "Successfully updated",
                                "id": updated.course_code}), 201
        except Exception as error:
            return jsonify({"ERROR": str(error), "message": "Not updated"}), 400
    return jsonify(ERROR="Admin only"), 403


@course_blueprint.route('/courses/<code>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_course(code):
    """function for delete endpoint, it handles course deletion"""
    if current_user.__tablename__ == 'admins':
        if len(current_user.roles) < 1:
            return jsonify(STATURS='No role assigned'), 401
        for role in current_user.roles:
            if not (role.role_name == 'super admin'):
                return jsonify(ERROR="Missing privilleges"), 401
        try:
            db_controller.delete(Course, code)
        except NoResultFound as e:
            return jsonify(error=str(e)), 400
        return jsonify(message="Successfully deleted course"), 200
    return jsonify(ERROR="Admins only")


def find_course_scores(code):
    """find scores that related to course"""
    all_scores = []
    course = db_controller.get_by_id(Course, code)
    scores = course.scores
    for score in scores:
        all_scores.append(score.to_dict())
    return all_scores


def find_department_with_course(code):
    """find department that has current course"""
    all_depts = []
    course = db_controller.get_by_id(Course, code)
    depts = course.departments
    for dept in depts:
        all_depts.append(dept.to_dict())
    return all_depts


def find_crs_materials(code):
    """find course materials"""
    all_materials = []
    course = db_controller.get_by_id(Course, code)
    materials = course.materials
    for mat in materials:
        all_materials.append(mat.to_dict())
    return all_materials
