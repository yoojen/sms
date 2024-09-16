from flask import Blueprint

course_blueprint = Blueprint(
    'course_blueprint', __name__, url_prefix='/api/v1')

dept_blueprint = Blueprint('dept_blueprint', __name__, url_prefix='/api/v1')

assignm_blueprint = Blueprint(
    'assignm_blueprint', __name__, url_prefix='/api/v1')
comm_blueprint = Blueprint('comm_blueprint', __name__, url_prefix='/api/v1')

material_blueprint = Blueprint(
    'material_blueprint', __name__, url_prefix='/api/v1')

roles_n_admin_bp = Blueprint(
    'roles_n_admin_bp', __name__, url_prefix='/api/v1')

score_blueprint = Blueprint('score_blueprint', __name__, url_prefix='/api/v1')

students_blueprint = Blueprint(
    "students_blueprint", __name__, url_prefix='/api/v1')

submission_bp = Blueprint('submission_bp', __name__, url_prefix='/api/v1')

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/api/v1')

degree_bp = Blueprint("degree_bp", __name__, url_prefix='/api/v1')

auth_blueprint = Blueprint("auth_blueprint", __name__, url_prefix='/api/v1')
