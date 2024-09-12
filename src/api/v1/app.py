from flask import Flask, jsonify

# from flask_login import LoginManager, login_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin


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
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SAMESITE"] = "None"
app.config["JWT_COOKIE_SECURE"] = True
app.config['JWT_COOKIE_HTTPONLY'] = True
app.config['JWT_COOKIE_DOMAIN'] = f'{HOST}:5000'
app.config["JWT_COOKIE_CSRF_PROTECT"]= False

app.config['CORS_SUPPORTS_CREDENTIALS'] = True  # Allow cookies in cross-origin requests

app.config["JWT_SECRET_KEY"] = "jwt yoojen signed key"

jwt = JWTManager(app=app)
# apply CORS
CORS(
    app, resources={r"/api/v1/*": {"origins": "*"}},
    supports_credentials=True
    )


"""
This configuration is regarding to flask_login which I'm not going to use
Now I'm going to use flask-jwt-extended for reactjs authentication and authorization

app.config['SECRET_KEY'] = 'randomly generated code'
# Default is 'session'
app.config['SESSION_COOKIE_NAME'] = 'lg-id'
# Ensures cookies are not accessible via JavaScript
app.config['SESSION_COOKIE_HTTPONLY'] = True
# Set to True in production to enforce HTTPS
app.config['SESSION_COOKIE_SECURE'] = False

course_blueprint.route = login_required(
    course_blueprint.route)  # Wrap the route decorator
login_manager = LoginManager()
login_manager.login_view = 'auth_blueprint.login'
login_manager.init_app(app)
"""

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


"""
This was used when Reactjs was yet to be used as frontend technology

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
"""

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from models.students import Student
    from models.teachers_and_degree import Teacher
    from models.roles_and_admins import Admin
    identity = jwt_data["sub"]
    user = db.get_by_email(Student, email=identity)
    user = db.get_by_email(Teacher, email=identity) if user is None else user
    user = db.get_by_email(Admin, email=identity) if user is None else user
    return user

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



if __name__ == "__main__":
    app.run(HOST, PORT, debug=True, threaded=True)
