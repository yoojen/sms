from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime

Base = declarative_base()


class BaseModel:
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    created_at = Column(
        DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow(), nullable=False)

    def to_json(self) -> dict:
        new_dict = {}
        new_dict = self.__dict__
        if hasattr(self, '_sa_instance_state'):
            del new_dict['_sa_instance_state']
        if hasattr(self, 'password'):
            new_dict['password'] = "***"
        return new_dict

    def __str__(self) -> str:
        return f"object: {self.__class__}"
