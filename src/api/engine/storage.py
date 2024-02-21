from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from sqlalchemy.exc import NoResultFound

from models.courses_departments import (Department,
                                        Course,
                                        DepartmentCourse)
from models.teachers_and_degree import (Teacher,
                                        Degree,
                                        TeacherDegree)
from models.teacher_dept import TeacherDepartments
from models.roles_and_admins import (Role,
                                     Admin,
                                     RoleAdmin)
from models.teacher_course import TeacherCourse
from models.assignments import Assignment
from models.materials_and_matdept import (Material,
                                          MaterialDepartments)
from models.communications import Communication
from models.submissions import Submission
from models.students import Student
from models.scores import Score


class DB:
    """all db operations are handled here"""
    _session = None
    _engine = None
    classes = {
        "Material": Material,
        "MaterialDepartments": MaterialDepartments,
        "Communication": Communication,
        "TeacherCourse": TeacherCourse,
        "RoleAdmin": RoleAdmin,
        "Admin": Admin,
        "Role": Role,
        "Teacher": Teacher,
        "Degree": Degree,
        "TeacherDegree": TeacherDegree,
        "TeacherDepartments": TeacherDepartments,
        "Assignment":  Assignment,
        "Department": Department,
        "Student": Student,
        "Course": Course,
        "DepartmentCourse": DepartmentCourse,
        "Submission": Submission,
        "Score": Score
    }

    def __init__(self) -> None:
        """create engine when it is called"""
        self._engine = create_engine('sqlite:///sims.db', echo=False)

    def reload(self) -> None:
        """connect python client to sqlite3 data storage"""
        # Base.metadata.drop_all(bind=self._engine)
        Base.metadata.create_all(bind=self._engine)
        session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=True)
        Session = scoped_session(session_factory)
        self._session = Session()

    def create_object(self, obj) -> Dict:
        """create new object in the database"""
        if type(obj) in self.classes.values():
            self._session.add(obj)
            self._session.commit()
            return obj
        else:
            return f'{obj.__repr__} not in known classes'

    def get_all_object(self, cls) -> Dict:
        """Query object from the database based on cls"""
        objs = {}
        if cls in self.classes.values():
            self._session.close()
            self._session.begin()
            objs = self._session.query(cls).all()
        return objs

    def get_by_id(self, cls,  id: str) -> Dict:
        """Query object from the database based on id provided as param"""
        obj = {}

        if cls in self.classes.values():
            if (cls == self.classes['Course']):
                obj = self._session.query(cls).filter(
                    cls.course_code == id).first()
            elif (cls == self.classes['Department']):
                obj = self._session.query(cls).filter(
                    cls.dept_code == id).first()
            elif (cls == self.classes['Student']):
                obj = self._session.query(cls).filter(
                    cls.regno == id).first()
            else:
                obj = self._session.query(cls).filter(cls.id == id).first()
        return obj

    def update(self, cls, id: str, **kwargs) -> Dict:
        """update the object in the databse using provided
        id and data as params
        """
        if cls in self.classes.values():
            obj = self.get_by_id(cls, id)
            if obj:
                for k, v in kwargs.items():
                    if obj.__dict__.get(k) == v:
                        raise ValueError("can not be the same")
                    setattr(obj, k, v)
                    self._session.commit()
            else:
                raise NoResultFound('Object with that id not found')
            return obj
        else:
            raise NoResultFound('Model not found')

    def delete(self, cls, id: str) -> bool:
        """delete item in the database which matches id 
        prvovided in function params
        """
        if cls in self.classes.values():
            obj = self.get_by_id(cls, id)
            if obj:
                self._session.delete(obj)
                self._session.commit()
                return True
            else:
                raise NoResultFound('Object with that id not found')
        else:
            raise NoResultFound('Model not found')
