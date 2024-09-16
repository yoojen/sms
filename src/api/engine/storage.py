from typing import Any, Dict

import bcrypt
from models.models import *
from models import db


class DBCONTROLLER:
    """all db operations are handled here"""

    def create_object(self, obj) -> Any:
        """create new object in the database"""
        try:
            db.session.add(obj)
            db.session.commit()
            return obj
        except Exception as e:
            return str(e), False

    def get_all_object(self, cls) -> Dict:
        """Query object from the database based on cls"""
        objs = db.session.query(cls).all()
        return objs

    def get_by_id(self, cls,  id: str):
        """Query object from the database based on id provided as param"""
        obj = {}
        try:
            if cls == Course:
                obj = db.session.query(cls).filter(
                    cls.course_code == id).first()
            elif cls == Department:
                obj = db.session.query(cls).filter(
                    cls.dept_code == id).first()
            elif cls == Student:
                obj = db.session.query(cls).filter(
                    cls.regno == id).first()
            else:
                obj = db.session.query(cls).filter(cls.id == id).first()
            return obj
        except:
            return None
    
    def update(self, cls, id: str, **kwargs) -> Dict:
        """update the object in the databse using provided
        id and data as params
        """
        obj = self.get_by_id(cls, id)
        if obj:
            for k, v in kwargs.items():
                if k == 'password':
                    print("It is password")
                    password_bytes = v.encode()
                    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                    setattr(obj, k, hashed_password)
                    continue
                if hasattr(obj, k):
                    setattr(obj, k, v)
            db.session.add(obj)
            db.session.commit()

        return obj

    def delete(self, cls, id: str) -> bool:
        """delete item in the database which matches id 
        prvovided in function params
        """
        obj = self.get_by_id(cls, id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        else:
            return False

    def search_all(self, cls, **kwargs):
        """search an item from db based on passed kwargs and cls(Class)"""
        objects = db.session.query(cls).filter_by(**kwargs).all()
        if objects:
            return objects
        else:
            return None
    
    def search_one(self, cls, **kwargs):
        """search an item from db based on passed kwargs and cls(Class)"""
        object = db.session.query(cls).filter_by(**kwargs).first()
        return object
    