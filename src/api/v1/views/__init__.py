from flask import Blueprint

course_blueprint = Blueprint(
    'course_blueprint', __name__, url_prefix='/api/v1')
dept_blueprint = Blueprint('dept_blueprint', __name__, url_prefix='/api/v1')
