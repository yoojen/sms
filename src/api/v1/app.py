from flask import Flask, jsonify
from flask_login import LoginManager, login_required
from api.engine import db
from api.v1.views import (course_blueprint,
                          dept_blueprint,
                          assignm_blueprint,
                          comm_blueprint,
                          material_blueprint,
                          roles_n_admin_bp,
                          score_blueprint,
                          students_blueprint,
                          submission_bp,
                          teacher_bp,
                          degree_bp,
                          auth_blueprint)

HOST = '127.0.0.1'
PORT = 5000
app = Flask(__name__)
app.config['SECRET_KEY'] = 'not secret'
course_blueprint.route = login_required(
    course_blueprint.route)  # Wrap the route decorator
login_manager = LoginManager()
login_manager.login_view = 'auth_blueprint.login'
login_manager.init_app(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(course_blueprint)
app.register_blueprint(dept_blueprint)
app.register_blueprint(assignm_blueprint)
app.register_blueprint(comm_blueprint)
app.register_blueprint(material_blueprint)
app.register_blueprint(roles_n_admin_bp)
app.register_blueprint(score_blueprint)
app.register_blueprint(students_blueprint)
app.register_blueprint(submission_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(degree_bp)


@login_manager.user_loader
def load_user(user_id):
    from models.students import Student
    from models.teachers_and_degree import Teacher
    from models.roles_and_admins import Admin
    student = db.get_by_id(Student, user_id)
    teacher = db.get_by_id(Teacher, user_id)
    admin = db.search(Admin, email=user_id)
    if student:
        return student
    if teacher:
        return teacher
    if admin:
        return admin[0]


@app.teardown_appcontext
def teardown_app(code):
    '''
        Handles teardown
    '''
    db.close()


@app.errorhandler(404)
def not_found_handler(error):
    """handler for not found error"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(403)
def forbiden_handler(error):
    """Forbiden error handler"""
    return jsonify({"error": "Forbiden"}), 401


@app.errorhandler(401)
def unauthorized_handler(error):
    """Unauthorized handler"""
    return jsonify({"error": "Unauthorized"}), 403
# from flask_login import login_required
# g.login_required = login


if __name__ == "__main__":
    app.run(HOST, PORT, debug=True, threaded=True)
