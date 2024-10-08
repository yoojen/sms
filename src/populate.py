from api.v1.app import app
from datetime import datetime
from models.models import *
from api.engine import db_controller
db = db_controller


with app.app_context():
    eugene = Student(regno=221003870, first_name="MUTUYIMANA", last_name="Eugene", tel='0720921921',
                     email="eugene@yahoo.com", password="Eugene123", dob=datetime.utcnow(),
                     dept_id=4, year_of_study=3, citizenship="Rwanda")
    created = db.create_object(eugene)
    admin = Admin(first_name="Eugene",
                  last_name="Mutuyimana",
                  email="yoojen@google.com", tel='0781231232', citizenship="Nigeria",
                  password="test", dob=datetime.utcnow(),
                  last_login=datetime.utcnow())

    db.create_object(admin)

    tchr = Teacher(
        first_name='Mushimwe',
        last_name='Jean',
        email='jean@google.com',
        password="google.123", tel='0781344312', citizenship='Uganda',
        dob=datetime.utcnow(),
        staff_member=False)

    created = db.create_object(tchr)

    dept = Department(dept_code='BIT', dept_name='BUSINESS INFORMATION TECHNOLOGY',
                      duration=3, trimester_or_semester='Trimester', credits=480, n_teachers=12, hod=tchr.id)
    db.create_object(dept)

    comm = Communication(teacher_id=tchr.id, dept_id=dept.dept_code, year_of_study=3,
                         message='we are having exams this coming monday')
    db.create_object(comm)

    course = Course(course_code="BIT4233", course_name="BIG DATA AND SOCIAL MEDIA", credits=20, year_of_study=3,
                    start_date=datetime.utcnow(), end_date=datetime.utcnow(), created_by=admin.id)

    db.create_object(course)

    assgn = Assignment(teacher_id=2,
                       dept_id="BBA",
                       course_id="BIT3211", assign_title="analysing data",
                       year_of_study=3, due_date=datetime.utcnow(), link="/home")

    db.create_object(assgn)

    azero = Degree(degree_name="Masters")
    db.create_object(azero)

    dept_course = DepartmentCourse(
        dept_id=dept.dept_code, course_id=course.course_code, date_assigned=datetime.utcnow())
    db.create_object(dept_course)

    mat = Material(course_code=course.course_code, teacher_id=tchr.id,
                   description="Big data book", link='/bit/big_data')

    db.create_object(mat)

    mat_dept = MaterialDepartments(
        material=mat, department=dept, date_uploaded=datetime.utcnow())
    db.create_object(mat_dept)

    role = Role(role_name="super admin")
    db.create_object(role)
    new_role = RoleAdmin(admin=admin, role=role,
                         date_granted=datetime.utcnow())
    db.create_object(new_role)

    # student = Student(regno=221104353,
    #                   first_name='Neza',
    #                   last_name='Neda',
    #                   email='no@google.com',
    #                   password='mepass',
    #                   dob=datetime.utcnow(),
    #                   department=dept.dept_code,
    #                   year_of_study=3,
    #                   citizenship="Rwanda")
    # db.create_object(student)
    score = Score(teacher_id=tchr.id, student_id=eugene.regno, dept_id=dept.dept_code,
                  course_code=course.course_code, assign_score=15, cat_score=30, exam_score=45)

    db.create_object(score)

    subm = Submission(student_id=eugene.regno,
                      assign_id=assgn.id, year_of_study=3, link='/rmt/submission')

    db.create_object(subm)

    tch_course = TeacherCourse(teacher=tchr, course=course,
                               date_assigned=datetime.utcnow())

    db.create_object(tch_course)

    tchr_dept = TeacherDepartments(
        teacher=tchr, department=dept, date_assigned=datetime.utcnow())
    db.create_object(tchr_dept)
    tchr_degree = TeacherDegree(teacher=tchr, degree=azero)
    db.create_object(tchr_degree)
    # --

    dept = db.get_by_id(Department, 'BIT')
    yoojen = db.get_by_id(Admin, 1)

    tchr = Teacher(
        first_name='Mushimwe',
        last_name='Jean',
        email='jean@google.com',
        password="google.123",
        dob=datetime.utcnow(),
        staff_member=False)

    created = db.create_object(tchr)

    # print(created)
    # # subs = db.get_all_object(Student)

    # tchr = db.get_by_id(Teacher, 1)
    azero = Degree(degree_name="Masters")
    db.create_object(azero)
    # azero = db.get_by_id(Degree, 1)
    # tchr_degree = TeacherDegree(teacher=tchr, degree=azero)
    db.create_object(tchr_degree)
    # print(tchr.degrees[0].degree_name)
    # db.delete(Degree, 1)
