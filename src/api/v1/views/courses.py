from models.courses_departments import Course, Department, DepartmentCourse
from api.v1.views import course_blueprint
from api.engine import db
from flask import flash, jsonify, redirect, request, url_for
from datetime import date, datetime
from models.base_model import BaseModel
from sqlalchemy.exc import NoResultFound
from flask_login import current_user, login_required

from models.students import Student
BASE_URL = 'http://localhost:5000/api/v1'


@course_blueprint.route('/courses', methods=['GET'], strict_slashes=False)
def courses():
    """returns all courses objects from the db"""
    new_obj = {}
    all_courses = []
    courses = db.get_all_object(Course)
    try:

        for course in courses:
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

            for k, v in course.to_json().items():
                if k in ['course_code', 'year_of_study', 'end_date', 'description',
                         'created_at', 'course_name', 'credits', 'start_date',
                         'created_by', 'updated_at']:
                    new_obj[k] = v
            new_obj['departments'] = departments
            new_obj['materials'] = materials
            new_obj['teachers'] = teachers
            new_obj['creator'] = creator
            if current_user.__tablename__ == 'admins':
                all_courses.append(new_obj)
            elif current_user.__tablename__ == 'teachers':
                if course in current_user.courses:
                    all_courses.append(new_obj)
            if current_user.__tablename__ == 'students':
                if current_user.department in course.departments:
                    all_courses.append(new_obj)
            new_obj = {}
    except Exception as error:
        flash("Login and try again")
        return redirect(url_for('auth_blueprint.login')), 301

    return jsonify({"courses": all_courses}), 200


@course_blueprint.route('/courses/<code>', methods=['GET'], strict_slashes=False)
def courses_by_code(code):
    """endpoint that handle retrival of course by is code"""
    new_obj = {}
    course = db.get_by_id(Course, code)
    try:
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

            if current_user.__tablename__ == 'admins':
                """display course based on admin credentials"""
                for k, v in course.to_json().items():
                    if k in ['course_code', 'year_of_study', 'end_date', 'description',
                             'created_at', 'course_name', 'credits', 'start_date',
                             'created_by', 'updated_at']:
                        new_obj[k] = v
                new_obj['departments'] = departments
                new_obj['materials'] = materials
                new_obj['teachers'] = teachers
                new_obj['creator'] = creator
            if current_user.__tablename__ == 'teachers':
                if course in current_user.courses:
                    for k, v in course.to_json().items():
                        if k in ['course_code', 'year_of_study', 'end_date', 'description',
                                 'created_at', 'course_name', 'credits', 'start_date',
                                 'created_by', 'updated_at']:
                            new_obj[k] = v
                    new_obj['departments'] = departments
                    new_obj['materials'] = materials
                    new_obj['teachers'] = teachers
                    new_obj['creator'] = creator
                # return new_obj
            if current_user.__tablename__ == 'students':
                if current_user.department in course.departments and\
                        course.year_of_study == current_user.year_of_study:
                    for k, v in course.to_json().items():
                        if k in ['course_code', 'year_of_study', 'end_date', 'description',
                                 'created_at', 'course_name', 'credits', 'start_date',
                                 'created_by', 'updated_at']:
                            new_obj[k] = v
                    new_obj['departments'] = departments
                    new_obj['materials'] = materials
                    new_obj['teachers'] = teachers
                    new_obj['creator'] = creator

    except Exception as error:
        print(error)
        flash("Login and try again")
        return redirect(url_for('auth_blueprint.login'))
    return jsonify({"course": new_obj}), 200


@course_blueprint.route('/courses/', methods=['POST'], strict_slashes=False)
@login_required
def create_course():
    """function that handles creation endpoint for Course instance"""
    data = dict(request.form)

    # check creator existence
    from models.roles_and_admins import Admin
    admin = db.get_by_id(Admin, data['created_by'])
    if not admin:
        return jsonify(ERROR='Admin not exists')
    start_date = data['start_date'].split('-')
    end_date = data['end_date'].split('-')
    if current_user.__tablename__ == 'admins':
        try:
            data['start_date'] = date(int(start_date[0]), int(
                start_date[1]), int(start_date[2]))
            data['end_date'] = date(int(end_date[0]), int(
                end_date[1]), int(end_date[2]))
            # check if it exists
            find_couse = db.get_by_id(Course, data['course_code'])
            if find_couse:
                return jsonify(error="Course already exist")
            created = db.create_object(Course(**data))
        except ValueError as e:
            return jsonify({"message": "Not created", "error": str(e)}), 400
        return jsonify({"message": "Successfully updated",
                        "id": created.course_name}), 201
    return jsonify(ERROR="You should be admin"), 403


@course_blueprint.route('/courses/<code>', methods=['PUT'], strict_slashes=False)
@login_required
def update_course(code):
    """function that handles update endpoint for Course instance"""
    if current_user.__tablename__ == 'admins':
        for role in current_user.roles:
            if not (role.role_name == 'super admin') or (role.role_name == 'editor'):
                return jsonify(ERROR="Admin only"), 403
        try:
            course = db.get_by_id(Course, code)
            if course:
                data = request.form
                updated = db.update(Course, code, **data)
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
        for role in current_user.roles:
            if not (role.role_name == 'super admin'):
                return jsonify(ERROR="Admin only"), 403
        try:
            db.delete(Course, code)
        except NoResultFound as e:
            return jsonify(error=str(e)), 400
        return jsonify(message="Successfully deleted course"), 200
    return jsonify(ERROR="Admins only")


def find_course_scores(code):
    """find scores that related to course"""
    all_scores = []
    course = db.get_by_id(Course, code)
    scores = course.scores
    for score in scores:
        all_scores.append(score.to_json())
    return all_scores


def find_department_with_course(code):
    """find department that has current course"""
    all_depts = []
    course = db.get_by_id(Course, code)
    depts = course.departments
    for dept in depts:
        all_depts.append(dept.to_json())
    return all_depts


def find_crs_materials(code):
    """find course materials"""
    all_materials = []
    course = db.get_by_id(Course, code)
    materials = course.materials
    for mat in materials:
        all_materials.append(mat.to_json())
    return all_materials
