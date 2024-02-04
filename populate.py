from models.courses_departments import *
from models.teachers_and_degree import *
from models.teacher_dept import *
from models.roles_and_admins import *
from models.teacher_course import *
from models.assignments import *
from models.materials_and_matdept import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime, date


engine = create_engine("sqlite:///sims.db", echo=True)
factory = sessionmaker(bind=engine, expire_on_commit=True)
Session = scoped_session(factory)
session = Session()

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


"""
seraphin = Teacher(first_name="Tuyishime", last_name="Seraphin", email="seraphin@gmail.com", password="seraphin123", dob=date(1995, 4, 19), staff_member=False)
sera_zero = Degree(degree_name="Masters") 
seraphin_degree = TeacherDegree(teacher=seraphin, degree=sera_zero)     
session.add_all([seraphin, sera_zero]) 
session.commit()

teacher = Teacher(first_name="Karangwa", last_name="Jean Baptiste",
                  email="karangwa@gmai.com", password="karangwa123", dob=date(1985, 4, 19), staff_member=True)

a_zero = Degree(degree_name="A0")
teacher_azero = TeacherDegree(teacher=teacher, degree=a_zero)

session.add_all([teacher,
                a_zero])
seraphin_dept = TeacherDepartments(teacher=seraphin, department=dept, date_assigned=datetime.utcnow())
session.commit()"""

"""yoojen = Admin(first_name="Eugene",
               last_name="Mutuyimana",
               email="yoojen@google.com",
               password="test", dob=datetime.utcnow(),
               last_login=datetime.utcnow())


super_admin = Role(role_name="super admin")

role_admin = RoleAdmin(admin=yoojen, role=super_admin,
                       date_granted=str(datetime.utcnow()))
session.add_all([yoojen, super_admin])
session.commit()
"""

"""
dept_course = DepartmentCourse(
    dept_id=dept.dept_code, course_id=course.course_code, date_assigned=datetime.utcnow())
course = Course(course_code="BIT1234", course_name="Big data", credits=20, year_of_study=3,
                start_date=datetime.utcnow(), end_date=datetime.utcnow(), created_by="5152f7dc-ecf2-4e07-a574-2a4fa32ba7ec")
dept = Department(
    dept_code="LAW",
    dept_name="Law",
    duration=4,
    trimester_or_semester="Trimester",
    credits=480,
    n_teachers=12,
    hod="5152f7dc-ecf2-4e07-a574-2a4fa32ba7ec"
)
"""


mat = Material(course_code="BIT1234", teacher_id="5152f7dc-ecf2-4e07-a574-2a4fa32ba7ec",
               year_of_study=3, description="Big data book")
mat_dept = MaterialDepartments(
    material=mat, department=dept, date_uploaded=datetime.utcnow())
# one-to-many relationship
assgn = Assignment(teacher_id="5152f7dc-ecf2-4e07-a574-2a4fa32ba7ec", dept_id="5152f7dc-ecf2-4e07-a574-2a4fa32ba7ec",
                   course_id="BIT1234", assign_title="analysing data", year_of_study=3, due_date=datetime.utcnow())
session.add(assgn)
