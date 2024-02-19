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

    def __str__(self) -> str:
        return f"object: {self.__class__}"
