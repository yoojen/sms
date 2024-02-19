from flask import Flask, jsonify
from api.v1.views import course_blueprint
HOST = '127.0.0.1'
PORT = 5000
app = Flask(__name__)
app.register_blueprint(course_blueprint)


@app.route('/')
def home_handler():
    """home message"""
    return jsonify({"message": "Home route"})


@app.errorhandler(404)
def not_found_handler(error):
    """handler for not found error"""
    return jsonify({"error": "Not found"})


@app.errorhandler(403)
def forbiden_handler(error):
    """Forbiden error handler"""
    return jsonify({"error": "Forbiden"})


@app.errorhandler(401)
def unauthorized_handler(error):
    """Unauthorized handler"""
    return jsonify({"error": "Unauthorized"})


if __name__ == "__main__":
    app.run(HOST, PORT, debug=True)
