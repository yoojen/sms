from flask_login import login_required
from models.models import Communication, Department, Admin, Teacher
from api.v1.views import comm_blueprint
from api.engine import db_controller
from flask import abort, jsonify, request
from sqlalchemy.exc import NoResultFound
from flask_jwt_extended import current_user, jwt_required


BASE_URL = 'http://localhost:5000/api/v1'



@comm_blueprint.route('/communications', methods=['GET'], strict_slashes=False)
@jwt_required()
def communications():
    """returns all Communication objects from the db"""
    new_obj = {}
    all_comms = []
    if isinstance(current_user, Admin):
        comms = db_controller.get_all_object(Department)
    elif isinstance(current_user, Teacher):
        comms = current_user.communications
    else:
        comms = [comm for comm in current_user.department.communications if comm.year_of_study==current_user.year_of_study]
    for comm in comms:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}' if comm.departments else None
        # teacher = f'{BASE_URL}/teachers/{comm.teachers.id}' if comm.teachers else None
        teacher = comm.teachers.__dict__
        del teacher["_sa_instance_state"]
        del teacher["password"]
        for k, v in comm.to_dict().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        # new_obj['departments'] = departments
        all_comms.append(new_obj)
        new_obj = {}
    return jsonify({"communications": all_comms}), 200


@comm_blueprint.route('/communications/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def single_communication(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    holder_obj = {}
    comm = db_controller.get_by_id(Communication, id)
    if comm:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}'
        teacher = f'{BASE_URL}/teachers/{comm.teachers.id}'

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(comm, args_dict)
            return jsonify(data), status_code
        for k, v in comm.to_dict().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                holder_obj[k] = v
        holder_obj['teacher'] = teacher
        holder_obj['submissions'] = departments

        if current_user == 'admins':
            new_obj = holder_obj
        if current_user == 'teachers':
            if comm.teachers == current_user:
                new_obj = holder_obj
        if current_user == 'students':
            if comm.year_of_study == current_user.year_of_study\
                    and comm.dept_id == current_user.dept_id:
                new_obj = holder_obj
        return jsonify({"communication": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@comm_blueprint.route('/communications/', methods=['POST'], strict_slashes=False)
@login_required
def create_communication():
    """function that handles creation endpoint for Communication instance"""
    if current_user == 'students':
        abort(403)
    data = dict(request.form)
    # Check if teacher, department or course really exist
    teacher = db_controller.get_by_id(Teacher, data.get('teacher_id'))
    data['year_of_study'] = int(data.get('year_of_study'))
    if not teacher:
        return jsonify(ERROR='Teacher does not exists'), 404
    dept = db_controller.get_by_id(Department, data.get('dept_id'))
    if not dept:
        return jsonify(ERROR='Department does not exists'), 404

    # teacher to only depts he/she has right to
    if isinstance(current_user, Teacher):
        if dept.teachers != current_user:
            abort(403)
    try:
        created = db_controller.create_object(Communication(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return ({"message": "Successfully created",
             "MESSAGE": f"{created.message[:15]}..."}), 201


@comm_blueprint.route('/communications/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_communication(id):
    """function for delete endpoint, it handles Communication deletion"""
    if current_user == 'students':
        abort(403)
    comm = db_controller.get_by_id(Communication, id)
    if current_user == 'teachers':
        if comm.teachers != current_user:
            abort(403)
    try:
        db_controller.delete(Communication, id)
    except NoResultFound as e:
        return jsonify(ERROR=str(e)), 400
    return jsonify(message="Successfully deleted assignment"), 200


# helpers
def find_comm_departments(comm):
    """Find department scores"""
    depts = comm.departments
    return depts.to_dict()


def find_comm_teachers(comm):
    """find course that are associated with the department"""
    tchr = comm.teachers
    return tchr.to_dict()


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
