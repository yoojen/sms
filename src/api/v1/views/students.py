from models.students import Student
from api.v1.views import students_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'


@students_blueprint.route('/students', methods=['GET'], strict_slashes=False)
def students():
    """return all students in the storage"""
    new_obj = {}
    all_students = []
    students = db.get_all_object(Student)
    if students:
        for student in students:
            department = f'{BASE_URL}/departments/{student.department.dept_code }'
            scores = [score.to_json() for score in student.scores]
            submissions = [subm.to_json() for subm in student.submissions]

            for k, v in student.to_json().items():
                if k in ['regno', 'first_name', 'last_name',  'email', 'password',
                         'dob', 'dept_id', 'year_of_study', 'sponsorship', 'citizenship',
                         'last_login', 'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['submissions'] = submissions
            new_obj['scores'] = scores
            new_obj['department'] = department

            all_students.append(new_obj)
            new_obj = {}
        return jsonify({"students": all_students}), 200
    return jsonify(message="Nothing found"), 404


@students_blueprint.route('/students/<int:regno>', methods=['GET'], strict_slashes=False)
def single_students(regno):
    """return all students in the storage"""
    new_obj = {}
    student = db.get_by_id(Student, regno)
    if student:
        department = f'{BASE_URL}/departments/{student.department.dept_code }'
        scores = [score.to_json() for score in student.scores]
        submissions = [subm.to_json() for subm in student.submissions]

        for k, v in student.to_json().items():
            if k in ['regno', 'first_name', 'last_name',  'email', 'password',
                     'dob', 'dept_id', 'year_of_study', 'sponsorship', 'citizenship',
                     'last_login', 'created_at', 'updated_at']:
                new_obj[k] = v

        new_obj['submissions'] = submissions
        new_obj['scores'] = scores
        new_obj['department'] = department
        return jsonify({"students": new_obj}), 200
    return jsonify(message="Nothing found"), 404


@students_blueprint.route('/students', methods=['POST'],
                          strict_slashes=False)
def create_student():
    """function that handles creation endpoint for Student instance"""
    data = dict(request.form)
    if data.get('dob'):
        data['dob'] = datetime.strptime(data.get('dob'), BaseModel.DATE_FORMAT)
    try:
        # check if it exists
        find_Score = db.get_by_id(Student, data.get('regno'))
        if find_Score:
            return jsonify(error="Student already exist"), 409
        created = db.create_object(Student(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "email": created.email}), 201


@students_blueprint.route('/students/<int:regno>', methods=['PUT'],
                          strict_slashes=False)
def update_student(regno):
    """ function that handles update endpoint for Student instance"""
    try:
        data = dict(request.form)
        updated = db.update(Student, regno, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.email}), 201


@students_blueprint.route('/students/<int:regno>', methods=['DELETE'],
                          strict_slashes=False)
def delete_student(regno):
    """function for delete endpoint, it handles Student deletion"""

    try:
        db.delete(Student, regno)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted student"), 200
