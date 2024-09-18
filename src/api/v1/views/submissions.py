import os
from pathlib import Path
import re
from datetime import datetime

from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, set_access_cookies
from api.v1.utils.helpers import time_to_future
from models.models import (
    Assignment, Course, Department, Admin,
    Student, Submission, Teacher
)
from api.v1.views import submission_bp
from api.engine import db_controller
from flask_login import current_user, login_required
from flask import abort, jsonify, make_response, request, current_app
from sqlalchemy.exc import NoResultFound
from werkzeug.utils import secure_filename


BASE_URL = 'http://localhost:5000/api/v1'


@submission_bp.route('/submissions', methods=['GET'], strict_slashes=False)
@login_required
def submissions():
    """return all submissions in the storage"""
    new_obj = {}
    all_submissions = []
    subms = db_controller.get_all_object(Submission)
    if subms:
        for subm in subms:
            assignment = subm.assignment.to_json()
            student = subm.student.to_json()

            for k, v in subm.to_json().items():
                if k in ['id', 'course_code', 'dept_id',  'student_id',
                         'assign_id', 'file_path', 'year_of_study', 'link',
                         'created_at', 'updated_at']:
                    new_obj[k] = v

            if student.get('password'):
                student['password'] = "***"
            new_obj['student'] = student
            new_obj['assignment'] = assignment

            if isinstance(current_user, Admin):
                all_submissions.append(new_obj)
            if isinstance(current_user, Teacher):
                if subm.assignment.teacher_id == current_user.id:
                    all_submissions.append(new_obj)
            if isinstance(current_user, Student):
                if subm.student_id == current_user.regno:
                    all_submissions.append(new_obj)
            new_obj = {}
        return jsonify({"submissions": all_submissions}), 200
    return jsonify(message="Nothing found")


@submission_bp.route('/submissions/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def single_submission(id):
    """return single submission in the storage"""
    holder_old = {}
    new_obj = {}
    subm = db_controller.get_by_id(Submission, id)
    if subm:
        assignment = subm.assignment.to_json()
        student = subm.student.to_json()

        if student.get('password'):
            student['password'] = "***"
        holder_old['student'] = student
        holder_old['assignment'] = assignment

        for k, v in subm.to_json().items():
            if k in ['id', 'course_code', 'dept_id',  'student_id',
                     'assign_id', 'file_path', 'year_of_study',
                     'created_at', 'updated_at']:
                holder_old[k] = v

        holder_old['student'] = student
        holder_old['assignment'] = assignment
        if current_user.__tablename__ == 'admins':
            new_obj = holder_old
        if isinstance(current_user, Teacher):
            if subm.dept_id in current_user.dept_id:
                new_obj = holder_old
        if isinstance(current_user, Student):
            if subm.student_id == current_user.regno:
                new_obj = holder_old

        return jsonify({"student": new_obj}), 200
    return jsonify(message="Nothing found"), 200


@submission_bp.route('/submissions', methods=['POST'],
                     strict_slashes=False)
@login_required
def create_submission():
    """function that handles creation endpoint for Submission instance"""
    if isinstance(current_user, Teacher):
        abort(403)
    data = dict(request.form)
    assgn = db_controller.get_by_id(Assignment, int(data['assign_id']))
    student = db_controller.get_by_id(Student, int(data['student_id']))
    dept = db_controller.get_by_id(Department, data['dept_id'])
    course = db_controller.get_by_id(Course, data['course_code'])

    if not assgn:
        return jsonify(ERROR='Assignment not exists')
    if not student:
        return jsonify(ERROR='Student not exists')
    if not dept:
        return jsonify(ERROR='Department not exists')
    if not course:
        return jsonify(ERROR='Course not exists')
    try:
        if isinstance(current_user, Student):
            data['year_of_study'] = current_user.year_of_study
            data['student_id'] = current_user.regno
            data['dept_id'] = current_user.dept_id
        # check if it exists
        find_subm = db_controller.search(Submission, course_code=data['course_code'],
                                         dept_id=data['dept_id'], student_id=int(
            current_user.regno),
            assign_id=int(data['assign_id']))
        if find_subm:
            return jsonify(error="Submitted already"), 409
        created = db_controller.create_object(Submission(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "assignment": created.assignment.assign_title}), 201


@submission_bp.route('/submissions/<int:id>', methods=['DELETE'],
                     strict_slashes=False)
@login_required
def delete_submission(id):
    """function for delete endpoint, it handles Submission deletion"""
    if not isinstance(current_user, Admin):
        abort(403)
    try:
        db_controller.delete(Submission, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted"), 200


def allowed_file(filename):
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@submission_bp.route('/submissions/<int:id>/check/<dept>/<course>', methods=['GET', 'POST'],
                     strict_slashes=False)
@jwt_required()
def check_submission(id, dept, course):
    DEPT_LOCATION = COURSE_LOCATION = ''
    assign = db_controller.get_by_id(Assignment, id)
    BASE_LOCATION = current_app.config['UPLOAD_FOLDER']

    # Create department directory (check if it already exists)
    DEPT_LOCATION = Path(f"{BASE_LOCATION}/{dept}")
    os.makedirs(DEPT_LOCATION, exist_ok=True)

    # Create course directory in department (same checks)
    title = assign.assign_title
    formatted_title = re.sub(r'\s+', '_', title)
    COURSE_LOCATION = Path(f"{DEPT_LOCATION}/{course}/{formatted_title}")
    os.makedirs(COURSE_LOCATION, exist_ok=True)

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify(error='provide file'), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify(error='provide file'), 400
        if file and allowed_file(file.filename):
            try:

                student = db_controller.search_one(
                    Student, email=get_jwt_identity())
                # If already submitted
                sub = db_controller.search_one(
                    Submission, student_id=student.regno, assign_id=assign.id)
                if not sub:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(COURSE_LOCATION, filename))
                    db_controller.update(Assignment, assign.id,
                                         submitted=assign.submitted + 1)

                    submission = Submission(
                        student_id=student.regno,
                        assign_id=assign.id,
                        year_of_study=student.year_of_study,
                        link=os.path.join(COURSE_LOCATION, filename)
                    )
                    sub_obj = db_controller.create_object(submission)
                    return jsonify({"submitted": True, "assign_id": assign.id, "filename": filename})
                return jsonify({"submitted": False, "error": "Already submitted"}), 400
            except Exception as e:
                return jsonify(submitted=False, error=str(e)), 400
        return jsonify(error="Something wrong happened"), 400
