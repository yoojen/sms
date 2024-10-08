from api.v1.views import auth_blueprint
from flask import get_flashed_messages, jsonify, render_template, request, make_response
import bcrypt
from api.engine import db_controller
from models.models import Admin, Student, Teacher
from flask_login import login_user, current_user, login_required, logout_user
from flask_jwt_extended import (
    create_access_token, set_access_cookies,
    current_user, jwt_required, get_jwt_identity, unset_access_cookies
)


@auth_blueprint.route('/index')
@login_required
def index():
    if len(current_user.__dict__) > 1:
        return render_template('index.html', user=current_user)
    else:
        return render_template('index.html', last_name='')


@auth_blueprint.route('/login')
def login():
    messages = get_flashed_messages(with_categories=True)
    return render_template('login.html', messages=messages)


@auth_blueprint.route('/auth/user-info', methods=['GET'])
@jwt_required()
def get_user_infog():
    return jsonify({
        "is_logged": True,
        "user_email": get_jwt_identity(),
    })


@auth_blueprint.route('/login', methods=['POST'])
def post_login():
    data = dict(request.get_json())
    email = data['email']
    teacher = db_controller.search_one(Teacher, email=email)
    user = teacher if teacher else None
    user = db_controller.search_one(
        Student, email=email) if not user else user
    user = db_controller.search_one(
        Admin, email=email) if not user else user
    try:
        if user:
            if not bcrypt.checkpw(data['password'].encode(), user.password):
                return jsonify(error='Not valid password'), 400
            response = make_response(
                jsonify({'msg': 'logged in', "isLogged": True, "email": user.email}), 200)
            access_token = create_access_token(identity=user)
            set_access_cookies(response, access_token)
            return response
        return jsonify({"error": "User is not registered"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_blueprint.route('/signup')
def signup():
    return render_template('signup.html')


@auth_blueprint.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    response = make_response({"message": "logged out"})
    unset_access_cookies(response=response)

    return response
