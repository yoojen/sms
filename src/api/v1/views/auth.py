from api.engine import db
from api.v1.views import auth_blueprint
from flask import jsonify, redirect, render_template, request, url_for
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
    return render_template('login.html')


@auth_blueprint.route('/login', methods=['POST'])
def post_login():
    data = dict(request.get_json())
    email = data['email']
    teacher = db.search(Teacher, email=email)
    student = db.search(Student, email=email)
    admin = db.search(Admin, email=email)
    try:
        if admin:
            if not bcrypt.checkpw(data['password'].encode(), admin[0].password):
                return jsonify(ERROR='Not valid password'), 400
            login_user(admin[0])
            return {'msg': 'logged in'}
        if student:
            if not bcrypt.checkpw(data['password'].encode(), student[0].password):
                return jsonify(ERROR='Not valid password'), 400
            login_user(student[0])
            return {'msg': 'logged in'}
        if teacher:
            if not bcrypt.checkpw(data['password'].encode(), teacher[0].password):
                return jsonify(ERROR='Not valid password'), 400
            login_user(teacher[0])
            return {'msg': 'logged in'}
        if not teacher and not admin and not student:
            return jsonify(ERROR='Email not registered')
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
