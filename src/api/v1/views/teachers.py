from models.teachers_and_degree import Teacher
from api.v1.views import teacher_bp
from api.engine import db
import bcrypt
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound, PendingRollbackError
from models.base_model import BaseModel
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'


@teacher_bp.route('/teachers', methods=['GET'], strict_slashes=False)
def teachers():
    """return all Teacher instance from the storage"""
    new_obj = {}
    all_teachers = []
    teachers = db.get_all_object(Teacher)
    if teachers:
        for tchr in teachers:
            department = [
                f'{BASE_URL}/departments/{dept.dept_code }' for dept in tchr.departments]
            scored = [
                f'{BASE_URL}/scores/{score.id }' for score in tchr.scored]
            degrees = [
                f'{BASE_URL}/degrees/{degree.id }' for degree in tchr.degrees if degree]
            courses = [
                f'{BASE_URL}/courses/{course.course_code }' for course in tchr.courses]
            assignments = [
                f'{BASE_URL}/assignments/{assign.id }' for assign in tchr.assignments]
            communications = [
                f'{BASE_URL}/communications/{comm.id }' for comm in tchr.communications]
            materials = [
                f'{BASE_URL}/materials/{material.id }' for material in tchr.materials]

            for k, v in tchr.to_json().items():
                if k in ['id', 'first_name', 'last_name',  'email', 'password',
                         'dob', 'staff_member', 'last_login', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['courses'] = courses
            new_obj['degrees'] = degrees
            new_obj['materials'] = materials
            new_obj['scored'] = scored
            new_obj['department'] = department
            new_obj['communications'] = communications
            new_obj['assignments'] = assignments

            all_teachers.append(new_obj)
            new_obj = {}
        return jsonify({"teachers": all_teachers}), 200
    return jsonify(message="Nothing found"), 404


@teacher_bp.route('/teachers/<int:id>', methods=['GET'], strict_slashes=False)
def single_teacher(id):
    """return single Teacher instance from the storage"""
    new_obj = {}
    teacher = db.get_by_id(Teacher, id)
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

        for k, v in teacher.to_json().items():
            if k in ['id', 'first_name', 'last_name',  'email', 'password',
                     'dob', 'staff_member', 'last_login', 'created_at', 'updated_at']:
                new_obj[k] = v

        new_obj['courses'] = courses
        new_obj['materials'] = materials
        new_obj['scored'] = scored
        new_obj['department'] = department
        new_obj['communications'] = communications
        new_obj['assignments'] = assignments

        return jsonify({"teacher": new_obj}), 200
    return jsonify(message="Nothing found"), 404


@teacher_bp.route('/teachers', methods=['POST'],
                  strict_slashes=False)
def create_teacher():
    """function that handles creation endpoint for Teacher instance"""
    data = dict(request.form)
    if data.get('dob'):
        data['dob'] = datetime.strptime(data.get('dob'), BaseModel.DATE_FORMAT)
    if data.get('staff_member'):
        data['staff_member'] = True
    else:
        data['staff_member'] = False
    password_bytes = data.get('password').encode()
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    data['password'] = hashed_password
    try:
        # check if it exists
        created = db.create_object(Teacher(**data))
    except Exception as e:
        db._session.rollback()
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "email": created.email}), 201


@teacher_bp.route('/teachers/<int:id>', methods=['PUT'],
                  strict_slashes=False)
def update_teacher(id):
    """ function that handles update endpoint for Teacher instance"""
    data = dict(request.form)
    if data.get('staff_member'):
        data['staff_member'] = True
    print(data)
    try:
        updated = db.update(Teacher, id, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.email}), 201


@teacher_bp.route('/teachers/<int:id>', methods=['DELETE'],
                  strict_slashes=False)
def delete_teacher(id):
    """function for delete endpoint, it handles Teacher deletion"""

    try:
        db.delete(Teacher, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted a teacher"), 200
