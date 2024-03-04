from flask_login import login_required
from models.communications import Communication
from api.v1.views import comm_blueprint
from api.engine import db
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from flask_login import current_user


BASE_URL = 'http://localhost:5000/api/v1'
user = current_user


@comm_blueprint.route('/communications', methods=['GET'], strict_slashes=False)
@login_required
def communications():
    """returns all Communication objects from the db"""
    new_obj = {}
    all_comms = []
    comms = db.get_all_object(Communication)
    for comm in comms:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}' if comm.departments else None
        teacher = f'{BASE_URL}/teachers/{comm.teachers.id}' if comm.teachers else None

        for k, v in comm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['departments'] = departments

        if user == 'admins':
            all_comms.append(new_obj)
        if user == 'teachers':
            if comm.teachers == user:
                all_comms.append(new_obj)
        if user == 'students':
            if comm.year_of_study == user.year_of_study\
                    and comm.dept_id == user.dept_id:
                all_comms.append(new_obj)
        new_obj = {}
    return jsonify({"communications": all_comms}), 200


@comm_blueprint.route('/communications/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def single_communication(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    holder_obj = {}
    comm = db.get_by_id(Communication, id)
    if comm:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}'
        teacher = f'{BASE_URL}/teachers/{comm.teachers.id}'

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(comm, args_dict)
            return jsonify(data), status_code
        for k, v in comm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                holder_obj[k] = v
        holder_obj['teacher'] = teacher
        holder_obj['submissions'] = departments

        if user == 'admins':
            new_obj = holder_obj
        if user == 'teachers':
            if comm.teachers == user:
                new_obj = holder_obj
        if user == 'students':
            if comm.year_of_study == user.year_of_study\
                    and comm.dept_id == user.dept_id:
                new_obj = holder_obj
        return jsonify({"communication": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@comm_blueprint.route('/communications/', methods=['POST'], strict_slashes=False)
@login_required
def create_communication():
    """function that handles creation endpoint for Communication instance"""
    if user == 'students':
        abort(403)
    data = dict(request.form)
    # Check if teacher, department or course really exist
    from models.teachers_and_degree import Teacher
    from models.courses_departments import Department
    teacher = db.get_by_id(Teacher, data.get('teacher_id'))
    data['year_of_study'] = int(data.get('year_of_study'))
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db.get_by_id(Department, data.get('dept_id'))
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404

    # teacher to only depts he/she has right to
    if user == 'teachers':
        if dept.teachers != user:
            abort(403)
    try:
        created = db.create_object(Communication(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return ({"message": "Successfully created",
             "MESSAGE": f"{created.message[:15]}..."}), 201


@comm_blueprint.route('/communications/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_communication(id):
    """function for delete endpoint, it handles Communication deletion"""
    if user == 'students':
        abort(403)
    comm = db.get_by_id(Communication, id)
    if user == 'teachers':
        if comm.teachers != user:
            abort(403)
    try:
        db.delete(Communication, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted assignment"), 200


# helpers
def find_comm_departments(comm):
    """Find department scores"""
    depts = comm.departments
    return depts.to_json()


def find_comm_teachers(comm):
    """find course that are associated with the department"""
    tchr = comm.teachers
    return tchr.to_json()


def args_handler(comm, args):
    """handles request.args from url"""
    if len(args) > 1:
        return jsonify(message="Not implemented")
    if args.get('departments') == 'true':
        comm_depts = find_comm_departments(comm)
        status_code = 200
        return {"communication": comm.id,
                "departments": comm_depts}, status_code
    elif args.get('teachers') == 'true':
        comm_teacher = find_comm_teachers(comm)
        status_code = 200
        return {f"{comm.id} teacher": comm_teacher}, status_code
    else:
        status_code = 400
        return {"ERROR": "Not implemented"}, status_code
