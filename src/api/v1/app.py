from flask import Flask, jsonify
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
                          degree_bp)


HOST = '127.0.0.1'
PORT = 5000
app = Flask(__name__)
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


@app.route('/')
def home_handler():
    """home message"""
    return jsonify({"message": "Home route"}), 200


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
    app.run(HOST, PORT, debug=True)
