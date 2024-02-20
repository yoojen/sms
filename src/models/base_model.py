from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime

Base = declarative_base()


class BaseModel:
    DATE_FORMAT = '%d%m%Y, %H:%M:%S'
    created_at = Column(
        DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow(), nullable=False)

    def to_json(self) -> dict:
        new_dict = {}
        new_dict = self.__dict__
        del new_dict['_sa_instance_state']
        return new_dict

    def __str__(self) -> str:
        return f"object: {self.__class__}"
