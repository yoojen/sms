from models.courses_departments import Department
from api.v1.views import dept_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound


BASE_URL = 'http://localhost:5000/api/v1'


@dept_blueprint.route('/departments', methods=['GET'], strict_slashes=False)
def departments():
    """returns all deparments objects from the db"""

    new_obj = {}
    all_depts = []
    depts = db.get_all_object(Department)
    for dept in depts:
        courses = [
            f'{BASE_URL}/courses/{course.course_code}'
            for course in dept.courses]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in dept.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in dept.teachers]
        students = [
            f'{BASE_URL}/students/{student.regno}'
            for student in dept.students]
        communications = [
            f'{BASE_URL}/communications/{comm.id}'
            for comm in dept.communications]
        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in dept.submissions]
        scores = [
            f'{BASE_URL}/scores/{score.id}'
            for score in dept.scores]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in departments.assignments] yet to be implemented

        for k, v in dept.to_json().items():
            if k in ['dept_code', 'dept_name', 'duration', 'trimester_or_semester',
                     'n_teachers', 'hod', 'credits', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['courses'] = courses
        new_obj['materials'] = materials
        new_obj['teachers'] = teachers
        new_obj['students'] = students
        new_obj['communications'] = communications
        new_obj['submissions'] = submissions
        new_obj['scores'] = scores
        all_depts.append(new_obj)
        new_obj = {}
    return jsonify({"departments": all_depts}), 200


@dept_blueprint.route('/departments/<code>', methods=['GET'], strict_slashes=False)
def one_department(code):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    dept = db.get_by_id(Department, code)
    if dept:
        courses = [
            f'{BASE_URL}/courses/{course.course_code}'
            for course in dept.courses]
        materials = [
            f'{BASE_URL}/materials/{material.id}'
            for material in dept.materials]
        teachers = [
            f'{BASE_URL}/teachers/{teacher.id}'
            for teacher in dept.teachers]
        students = [
            f'{BASE_URL}/students/{student.regno}'
            for student in dept.students]
        communications = [
            f'{BASE_URL}/communications/{comm.id}'
            for comm in dept.communications]
        submissions = [
            f'{BASE_URL}/submissions/{subm.id}'
            for subm in dept.submissions]
        scores = [
            f'{BASE_URL}/scores/{score.id}'
            for score in dept.scores]
        # assignments = [f'{BASE_URL}/assignments/{assign.id}'
        # for assign in departments.assignments] yet to be implemented

        for k, v in dept.to_json().items():
            if k in ['dept_code', 'dept_name', 'duration', 'trimester_or_semester',
                     'n_teachers', 'hod', 'credits', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['courses'] = courses
        new_obj['materials'] = materials
        new_obj['teachers'] = teachers
        new_obj['students'] = students
        new_obj['communications'] = communications
        new_obj['submissions'] = submissions
        new_obj['scores'] = scores

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(dept, args_dict)
            return jsonify([data]), status_code
        return jsonify({"department": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@dept_blueprint.route('/departments/', methods=['POST'], strict_slashes=False)
def create_department():
    """function that handles creation endpoint for Department instance"""
    data = dict(request.form)
    try:
        # check if it exists
        find_dept = db.get_by_id(Department, data['dept_code'])
        if find_dept:
            return jsonify(error="Department already exist")
        created = db.create_object(Department(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return jsonify({"message": "Successfully created",
                    "id": created.dept_name}), 201


@dept_blueprint.route('/departments/<code>', methods=['PUT'], strict_slashes=False)
def update_department(code):
    """ function that handles update endpoint for Department instance"""
    try:
        data = request.form
        # print(data)
        updated = db.update(Department, code, **data)
    except Exception as error:
        return jsonify(ERROR=str(error)), 400
    return jsonify({"message": "Successfully updated",
                    "id": updated.dept_code}), 201


@dept_blueprint.route('/departments/<code>', methods=['DELETE'], strict_slashes=False)
def delete_department(code):
    """function for delete endpoint, it handles course deletion"""

    try:
        db.delete(Department, code)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted course"), 200


# helpers
def find_dept_scores(dept):
    """Find department scores"""
    all_scores = []
    scores = dept.scores
    for score in scores:
        all_scores.append(score.to_json())
    return all_scores


def find_dept_materials(dept):
    """find department materials"""
    all_materials = []
    materials = dept.materials
    for mat in materials:
        all_materials.append(mat.to_json())
    return all_materials


def find_dept_courses(dept):
    """find course that are associated with the department"""
    all_courses = []
    courses = dept.courses
    for course in courses:
        all_courses.append(course.to_json())
    return all_courses


def args_handler(dept, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('scores') == 'true':
        dept_scores = find_dept_scores(dept)
        status_code = 200
        return jsonify({"scores": {"department": dept.dept_code,
                                   "score": dept_scores}}), status_code
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
