from models.models import Admin, Teacher
from api.v1.views import teacher_bp
from api.engine import db_controller
import bcrypt
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound, PendingRollbackError
from datetime import date
from flask_login import current_user, login_required
from flask_jwt_extended import current_user, jwt_required

BASE_URL = 'http://localhost:5000/api/v1'


@teacher_bp.route('/teachers', methods=['GET'], strict_slashes=False)
# @login_required
def teachers():
    """return all Teacher instance from the storage"""
    if current_user.__tablename__ == 'students':
        abort(403)
    new_obj = {}
    all_teachers = []
    teachers = db_controller.get_all_object(Teacher)
    if teachers:
        for tchr in teachers:
            department = [
                f'{BASE_URL}/departments/{dept.dept_code }' for dept in tchr.departments if tchr.departments]
            scored = [
                f'{BASE_URL}/scores/{score.id }' for score in tchr.scored if tchr.scored]
            degrees = [
                f'{BASE_URL}/degrees/{degree.id }' for degree in tchr.degrees if degree]
            courses = [
                f'{BASE_URL}/courses/{course.course_code }' for course in tchr.courses if tchr.courses]
            assignments = [
                f'{BASE_URL}/assignments/{assign.id }' for assign in tchr.assignments if tchr.assignments]
            communications = [
                f'{BASE_URL}/communications/{comm.id }' for comm in tchr.communications if tchr.communications]
            materials = [
                f'{BASE_URL}/materials/{material.id }' for material in tchr.materials if tchr.materials]

            for k, v in tchr.to_dict().items():
                if k in ['id', 'first_name', 'last_name',  'email', 'citizenship', 'tel',
                         'dob', 'staff_member', 'last_login', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['courses'] = courses
            new_obj['degrees'] = degrees
            new_obj['materials'] = materials
            new_obj['scored'] = scored
            new_obj['department'] = department
            new_obj['communications'] = communications
            new_obj['assignments'] = assignments

            if current_user.__tablename__ == 'admins':
                all_teachers.append(new_obj)
            if current_user.__tablename__ == 'teachers':
                if tchr.id == current_user.id:
                    all_teachers.append(new_obj)
            new_obj = {}
        return jsonify({"teachers": all_teachers}), 200
    return jsonify([]), 200


@teacher_bp.route('/teachers/<int:id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def single_teacher(id):
    """return single Teacher instance from the storage"""
    # if current_user.__tablename__ == 'students':
    #     abort(403)
    new_obj = {}
    teacher = db_controller.get_by_id(Teacher, id)
    if teacher:
        department = [
            f'{BASE_URL}/departments/{dept.dept_code }' for dept in teacher.departments]
        scored = [
            f'{BASE_URL}/scores/{score.id }' for score in teacher.scored]
        courses = [f'{BASE_URL}/courses/{course.course_code }'
                   for course in teacher.courses]
        assignments = [f'{BASE_URL}/assignments/{assign.id }'
                       for assign in teacher.assignments]
        communications = [f'{BASE_URL}/communications/{comm.id }'
                          for comm in teacher.communications]
        materials = [
            f'{BASE_URL}/materials/{material.id }' for material in teacher.materials]

        if current_user.__tablename__ == 'admins':
            for k, v in teacher.to_dict().items():
                if k in ['id', 'first_name', 'last_name',  'email', 'citizenship', 'tel',
                         'dob', 'staff_member', 'last_login', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['courses'] = courses
            new_obj['materials'] = materials
            new_obj['scored'] = scored
            new_obj['department'] = department
            new_obj['communications'] = communications
            new_obj['assignments'] = assignments
        if current_user.__tablename__ == 'teachers':
            if teacher.id == current_user.id:
                for k, v in teacher.to_dict().items():
                    if k in ['id', 'first_name', 'last_name',  'email', 'citizenship', 'tel',
                             'dob', 'staff_member', 'last_login', 'created_at', 'updated_at']:
                        new_obj[k] = v

                new_obj['courses'] = courses
                new_obj['materials'] = materials
                new_obj['scored'] = scored
                new_obj['department'] = department
                new_obj['communications'] = communications
                new_obj['assignments'] = assignments

        return jsonify({"teacher": new_obj}), 200
    return jsonify([]), 200


@teacher_bp.route('/teachers', methods=['POST'],
                  strict_slashes=False)
@login_required
def create_teacher():
    """function that handles creation endpoint for Teacher instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    try:
        dob = data['dob'].split('-')
        data['dob'] = date(int(dob[0]), int(dob[1]), int(dob[2]))
        if data.get('staff_member'):
            data['staff_member'] = True
        else:
            data['staff_member'] = False
        password_bytes = data.get('password').encode()
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        data['password'] = hashed_password
        # check if it exists
        created = db_controller.create_object(Teacher(**data))
    except Exception as e:
        db_controller._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "email": created.email}), 201


@teacher_bp.route('/teachers/<int:id>', methods=['PUT'],
                  strict_slashes=False)
@login_required
def update_teacher(id):
    """ function that handles update endpoint for Teacher instance"""
    if not isinstance(current_user, Admin):
        abort(403)
    data = dict(request.form)
    if data.get('staff_member'):
        data['staff_member'] = True
    try:
        updated = db_controller.update(Teacher, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.email}), 201


@teacher_bp.route('/teachers/<int:id>', methods=['DELETE'],
                  strict_slashes=False)
@login_required
def delete_teacher(id):
    """function for delete endpoint, it handles Teacher deletion"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(Teacher, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted a teacher"), 200
