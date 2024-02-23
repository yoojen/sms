from models.submissions import Submission
from api.v1.views import submission_bp
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'


@submission_bp.route('/submissions', methods=['GET'], strict_slashes=False)
def submissions():
    """return all submissions in the storage"""
    # IT WILL HANDLE FILE THUMBNAIL DISPLAYING
    new_obj = {}
    all_submissions = []
    subms = db.get_all_object(Submission)
    if subms:
        for subm in subms:
            department = subm.department.to_json()
            assignment = subm.assignment.to_json()
            student = subm.student.to_json()

            for k, v in subm.to_json().items():
                if k in ['id', 'course_code', 'dept_id',  'student_id',
                         'assign_id', 'file_path', 'year_of_study',
                         'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['student'] = student
            new_obj['assignment'] = assignment
            new_obj['department'] = department

            all_submissions.append(new_obj)
            new_obj = {}
        return jsonify({"submissions": all_submissions}), 200
    return jsonify(message="Nothing found"), 404


@submission_bp.route('/submissions/<int:id>', methods=['GET'], strict_slashes=False)
def single_submission(id):
    """return single submission in the storage"""
    # IT WILL HANDLE FILE DOWNLOAD
    new_obj = {}
    subm = db.get_by_id(Submission, id)
    if subm:
        department = subm.department.to_json()
        assignment = subm.assignment.to_json()
        student = subm.student.to_json()

        for k, v in subm.to_json().items():
            if k in ['id', 'course_code', 'dept_id',  'student_id',
                     'assign_id', 'file_path', 'year_of_study',
                     'created_at', 'updated_at']:
                new_obj[k] = v

        new_obj['student'] = student
        new_obj['assignment'] = assignment
        new_obj['department'] = department

        return jsonify({"student": new_obj}), 200
    return jsonify(message="Nothing found"), 200


@submission_bp.route('/submissions', methods=['POST'],
                     strict_slashes=False)
def create_submission():
    """function that handles creation endpoint for Submission instance"""
    # THIS WILL HANDLE FILE UPLOAD
    data = dict(request.form)
    try:
        # check if it exists
        find_subm = db.get_by_id(Submission, data.get('id'))
        # I HAVE TO BUILD SOMETHING THAT I CAN CHECK ACCORDING
        # TO ASSIGNMENT ID AND STUDENT ID SO THAT I CAN KNOW
        # STUDENT ALREADY SUBMITTED
        if find_subm:
            return jsonify(error="Submitted already"), 409
        created = db.create_object(Submission(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "assignment": created.assignment.assign_title}), 201


@submission_bp.route('/submissions/<int:id>', methods=['DELETE'],
                     strict_slashes=False)
def delete_submission(id):
    """function for delete endpoint, it handles Submission deletion"""
    # IT WILL EVEN HANDLE FILE REMOVAL ON DISK
    try:
        db.delete(Submission, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted"), 200
