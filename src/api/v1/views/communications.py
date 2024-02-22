from models.communications import Communication
from api.v1.views import comm_blueprint
from api.engine import db
from flask import jsonify, request
from sqlalchemy.exc import NoResultFound
from models.base_model import BaseModel
from datetime import datetime


BASE_URL = 'http://localhost:5000/api/v1'


@comm_blueprint.route('/communications', methods=['GET'], strict_slashes=False)
def communications():
    """returns all Communication objects from the db"""

    new_obj = {}
    all_comms = []
    comms = db.get_all_object(Communication)
    for comm in comms:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}'
        teacher = f'{BASE_URL}/teachers/{comm.teachers.id}'

        for k, v in comm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['departments'] = departments
        all_comms.append(new_obj)
        new_obj = {}
    return jsonify({"communications": all_comms}), 200


@comm_blueprint.route('/communications/<int:id>', methods=['GET'], strict_slashes=False)
def single_communication(id):
    """ endpoint that handle retrival of department by is code"""
    new_obj = {}
    comm = db.get_by_id(Communication, id)
    if comm:
        departments = f'{BASE_URL}/departments/{comm.departments.dept_code}'
        teacher = f'{BASE_URL}/teachers/{comm.teachers.id}'

        for k, v in comm.to_json().items():
            if k in ['id', 'teacher_id', 'dept_id', 'year_of_study',
                     'message', 'created_at', 'updated_at']:
                new_obj[k] = v
        new_obj['teacher'] = teacher
        new_obj['submissions'] = departments

        # handling url args
        if request.args:
            args_dict = dict(request.args)
            data, status_code = args_handler(comm, args_dict)
            return jsonify(data), status_code
        return jsonify({"communication": new_obj}), 200
    else:
        return jsonify(ERROR="Not found"), 404


@comm_blueprint.route('/communications/', methods=['POST'], strict_slashes=False)
def create_communication():
    """function that handles creation endpoint for Communication instance"""
    data = dict(request.form)
    if data.get('year_of_study'):
        data['year_of_study'] = int(data.get('year_of_study'))
    try:
        created = db.create_object(Communication(**data))
    except ValueError as e:
        return jsonify({"message": "Not created", "error": str(e)}), 400
    return ({"message": "Successfully created",
             "MESSAGE": f"{created.message[:15]}..."}), 201


@comm_blueprint.route('/communications/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_communication(id):
    """function for delete endpoint, it handles Communication deletion"""

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
