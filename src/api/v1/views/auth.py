from api.engine import db
from api.v1.views import auth_blueprint
from flask import get_flashed_messages, jsonify, redirect, render_template, request, session, url_for
import bcrypt
from models.roles_and_admins import Admin
from models.students import Student
from flask_login import login_user, current_user, login_required, logout_user

from models.teachers_and_degree import Teacher


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


@auth_blueprint.route('/login', methods=['POST'])
def post_login():
    data = dict(request.get_json())
    email = data['email']
    teacher = db.get_by_email(Teacher, email=email)
    user = teacher  if teacher else None
    user = db.get_by_email(Student, email=email) if not user else user
    user = db.get_by_email(Admin, email=email) if not user else user
    try:
        if user:
            if not bcrypt.checkpw(data['password'].encode(), user.password):
                return jsonify(ERROR='Not valid password'), 400
            isLogged = login_user(user, remember=True)
            return {'msg': 'logged in', "isLogged": isLogged}
        return jsonify({"message": "User is not registered"})
       
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_blueprint.route('/signup')
def signup():
    return render_template('signup.html')


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()

    return jsonify(message='done')
