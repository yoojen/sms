from api.v1.authorize import find_dept, is_teacher
from models.assignments import Assignment
from models.courses_departments import Course, Department
from models.students import Student
from models.submissions import Submission
from api.v1.views import submission_bp
from api.engine import db
from flask_login import current_user, login_required
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from models.teachers_and_degree import Teacher

BASE_URL = 'http://localhost:5000/api/v1'


@submission_bp.route('/submissions', methods=['GET'], strict_slashes=False)
@login_required
def submissions():
    """return all submissions in the storage"""
    new_obj = {}
    all_submissions = []
    subms = db.get_all_object(Submission)
    if current_user.__tablename__ == 'students':
        # ass_tchr = current_user
        usr_dept = current_user.department
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
                del student['password']
            if student.get('assignment'):
                del student['assignment']
            if student.get('department'):
                del student['department']
            new_obj['student'] = student
            new_obj['assignment'] = assignment

            if current_user.__tablename__ == 'admins':
                all_submissions.append(new_obj)
            if current_user.__tablename__ == 'teachers':
                tch_dept = is_teacher(current_user.id)
                dept = find_dept(subm.dept_id)
                if dept in tch_dept:
                    new_obj['department'] = dept.to_json().get('dept_code')
                    all_submissions.append(new_obj)
            if current_user.__tablename__ == 'students':
                dept = find_dept(subm.dept_id)
                if usr_dept == dept \
                        and subm.student_id == current_user.regno:
                    all_submissions.append(new_obj)
            new_obj = {}
        return jsonify({"submissions": all_submissions}), 200
    return jsonify(message="Nothing found")


@submission_bp.route('/submissions/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def single_submission(id):
    """return single submission in the storage"""
    # IT WILL HANDLE FILE DOWNLOAD
    new_obj = {}
    subm = db.get_by_id(Submission, id)
    if subm:
        if current_user.__tablename__ == 'students':
            usr_dept = current_user.department
        assignment = subm.assignment.to_json()
        student = subm.student.to_json()

        if student.get('password'):
            del student['password']
        if student.get('assignment'):
            del student['assignment']
        if student.get('department'):
            del student['department']
        new_obj['student'] = student
        new_obj['assignment'] = assignment

        if current_user.__tablename__ == 'admins':
            for k, v in subm.to_json().items():
                if k in ['id', 'course_code', 'dept_id',  'student_id',
                         'assign_id', 'file_path', 'year_of_study',
                         'created_at', 'updated_at']:
                    new_obj[k] = v

            new_obj['student'] = student
            new_obj['assignment'] = assignment
        if current_user.__tablename__ == 'teachers':
            tch_dept = is_teacher(current_user.id)
            if subm.department in tch_dept:
                for k, v in subm.to_json().items():
                    if k in ['id', 'course_code', 'dept_id',  'student_id',
                             'assign_id', 'file_path', 'year_of_study',
                             'created_at', 'updated_at']:
                        new_obj[k] = v

                new_obj['student'] = student
                new_obj['assignment'] = assignment
        if current_user.__tablename__ == 'students':
            if usr_dept == subm.department \
                    and subm.student_id == current_user.regno:
                for k, v in subm.to_json().items():
                    if k in ['id', 'course_code', 'dept_id',  'student_id',
                             'assign_id', 'file_path', 'year_of_study',
                             'created_at', 'updated_at']:
                        new_obj[k] = v

        new_obj['student'] = student
        new_obj['assignment'] = assignment

        return jsonify({"student": new_obj}), 200
    return jsonify(message="Nothing found"), 200


@submission_bp.route('/submissions', methods=['POST'],
                     strict_slashes=False)
@login_required
def create_submission():
    """function that handles creation endpoint for Submission instance"""
    if current_user.__tablename__ != 'students':
        abort(403)
    data = dict(request.form)
    assgn = db.get_by_id(Assignment, int(data['assign_id']))
    student = db.get_by_id(Student, int(data['student_id']))
    dept = db.get_by_id(Department, data['dept_id'])
    course = db.get_by_id(Course, data['course_code'])

    if not assgn:
        return jsonify(ERROR='Assignment not exists')
    if not student:
        return jsonify(ERROR='Student not exists')
    if not dept:
        return jsonify(ERROR='Department not exists')
    if not course:
        return jsonify(ERROR='Course not exists')
    try:
        # check if it exists
        find_subm = db.search(Submission, course_code=data['course_code'],
                              dept_id=data['dept_id'], student_id=int(
                                  current_user.regno),
                              assign_id=int(data['assign_id']))
        if find_subm:
            return jsonify(error="Submitted already"), 409
        created = db.create_object(Submission(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "assignment": created.assignment.assign_title}), 201


@submission_bp.route('/submissions/<int:id>', methods=['DELETE'],
                     strict_slashes=False)
@login_required
def delete_submission(id):
    """function for delete endpoint, it handles Submission deletion"""
    if current_user.__tablename__ == 'students':
        abort(403)
    try:
        db.delete(Submission, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted"), 200
