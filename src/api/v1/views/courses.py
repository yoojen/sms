from api.v1.views import course_blueprint
from flask import jsonify


@course_blueprint.route('/courses', strict_slashes=False)
def courses():
    return jsonify({"msg": "all courses"})
