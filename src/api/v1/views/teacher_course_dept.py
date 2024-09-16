from flask_login import current_user
from models.models import (
    Course, Department, DepartmentCourse, BaseModel,
    Teacher, TeacherCourse, Admin
)
from api.v1.views import course_blueprint
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from flask_login import login_required

BASE_URL = 'http://localhost:5000/api/v1'


@course_blueprint.route('/teacher_course', methods=['GET'], strict_slashes=False)
@login_required
def teacher_course():
    """return all teacher and courses associations"""
    new_obj = {}
    all_associations = []
    tchr_dept_associations = db_controller.get_all_object(TeacherCourse)
    if tchr_dept_associations:
        for td in tchr_dept_associations:
            teacher = [
                td.teacher.to_json() if td.teacher else None]
            course = [
                td.course.to_json() if td.course else None]

            for k, v in td.to_json().items():
                if k in ['id', 'date_assigned',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['teacher'] = teacher
            new_obj['course'] = course
            all_associations.append(new_obj)
            new_obj = {}
        return jsonify({"teacher-course associations": all_associations}), 200
    else:
        return jsonify(ERROR='Nothing found'), 404


@course_blueprint.route('/teacher_course/<int:id>', methods=['GET'],
                        strict_slashes=False)
@login_required
def single_teacher_course(id):
    """return a teacher degree association based on teacher id"""
    new_obj = {}
    td = db_controller.get_by_id(TeacherCourse, id)
    if td:
        teacher = [
            td.teacher.to_json() if td.teacher else None]
        course = [
            td.course.to_json() if td.course else None]

        for k, v in td.to_json().items():
            if k in ['id', 'date_assigned',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['course'] = course
        return jsonify({"td association": new_obj}), 200
    else:
        return jsonify(ERROR="Nothing found")


@course_blueprint.route('/teacher_course', methods=['POST'], strict_slashes=False)
@login_required
def create_teacher_association():
    """create a teacher course association instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)

    teacher = db_controller.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404

    course = db_controller.get_by_id(Course, data['course_code'])
    if not course:
        return jsonify(ERROR='Course does not exists'), 404

    if data.get('date_assigned'):
        data['date_assigned'] = datetime.strptime(
            data['date_assigned'], BaseModel.DATE_FORMAT)
    data['teacher_id'] = int(data.get('teacher_id'))
    try:
        # check if it exists
        assoc = db_controller.search(TeacherCourse, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        created = db_controller.create_object(TeacherCourse(**data))
    except Exception as e:
        db_controller._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@course_blueprint.route('/teacher_course/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_association_object(id):
    """update teacher degree association object"""

    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    if data.get('teacher_id'):
        data['teacher_id'] = int(data['teacher_id'])

    teacher = db_controller.get_by_id(Teacher, data['teacher_id'])
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    crs = db_controller.get_by_id(Department, data['course_code'])
    if not crs:
        return jsonify(ERROR='Course does not exists'), 404
    try:
        assoc = db_controller.search(TeacherCourse, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        data['updated_at'] = datetime.utcnow()
        updated = db_controller.update(TeacherCourse, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@course_blueprint.route('/teacher_course/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_association(id):
    """remove association between degree and teacher"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(TeacherCourse, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200


# course and department association endpoints
@course_blueprint.route('/dept_course', methods=['GET'], strict_slashes=False)
@login_required
def dept_course():
    """return all department and courses associations"""
    new_obj = {}
    all_associations = []
    dept_crs_associations = db_controller.get_all_object(DepartmentCourse)
    if dept_crs_associations:
        for td in dept_crs_associations:
            department = [
                td.department.to_json() if td.department else None]
            course = [
                td.course.to_json() if td.course else None]

            for k, v in td.to_json().items():
                if k in ['id', 'date_assigned',
                         'created_at', 'updated_at']:
                    new_obj[k] = v
            new_obj['department'] = department
            new_obj['course'] = course
            all_associations.append(new_obj)
            new_obj = {}
        return jsonify({"department-course associations": all_associations}), 200
    else:
        return jsonify(ERROR='Nothing found'), 404


@course_blueprint.route('/dept_course/<int:id>', methods=['GET'],
                        strict_slashes=False)
@login_required
def single_dept_course(id):
    """return a department-course association based on teacher id"""
    new_obj = {}
    td = db_controller.get_by_id(DepartmentCourse, id)
    if td:
        department = [
            td.department.to_json() if td.department else None]
        course = [
            td.course.to_json() if td.course else None]

        for k, v in td.to_json().items():
            if k in ['id', 'date_assigned',
                     'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['department'] = department
        new_obj['course'] = course
        return jsonify({"crs-dept association": new_obj}), 200
    else:
        return jsonify(ERROR="Nothing found")


@course_blueprint.route('/dept_course', methods=['POST'], strict_slashes=False)
@login_required
def create_crs_dept_association():
    """create a department-course association instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    dept = db_controller.get_by_id(Department, data['dept_id'])
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404
    course = db_controller.get_by_id(Course, data['course_id'])
    if not course:
        return jsonify(ERROR='Course does not exists'), 404

    if data.get('date_assigned'):
        data['date_assigned'] = datetime.strptime(
            data['date_assigned'], BaseModel.DATE_FORMAT)
    try:
        # check if it exists
        assoc = db_controller.search(DepartmentCourse, **data)
        if assoc:
            return jsonify(ERROR='Association alredy exists'), 409
        created = db_controller.create_object(DepartmentCourse(**data))
    except Exception as e:
        db_controller._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created", "id": created.id}), 201


@course_blueprint.route('/dept_course/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_dept_crs(id):
    """update department-course association object"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    if data.get('dept_id'):
        dept = db_controller.get_by_id(Department, data['dept_id'])
        if not dept:
            return jsonify(ERROR='Department does not exists'), 404
    if data.get('course_id'):
        course = db_controller.get_by_id(Course, data['course_id'])
        if not course:
            return jsonify(ERROR='Course does not exists'), 404

    try:
        data['updated_at'] = datetime.utcnow()
        updated = db_controller.update(DepartmentCourse, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.id}), 201


@course_blueprint.route('/dept_course/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def remove_dept_crs(id):
    """remove association between department-course"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(DepartmentCourse, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted an association"), 200
