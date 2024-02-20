from models.courses_departments import Department
from api.v1.views import dept_blueprint
from api.engine import db
from flask import jsonify


@dept_blueprint.route('/departments', strict_slashes=False)
def depts():
    """returns all courses objects from the db"""
    depts_list = []
    depts = db.get_all_object(Department)
    for dept in depts:
        depts_list.append(dept.to_json())
    return jsonify({"departments": depts_list})


@dept_blueprint.route('/departments/<code>', strict_slashes=False)
def dept_by_code(code):
    dept = db.get_by_id(Department, code)
    if dept:
        dept.to_json()
    return jsonify({"department": dept})
