from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime

Base = declarative_base()


class BaseModel:
    DATE_FORMAT = '%d%m%Y, %H:%M:%S'

    id = Column(String(50), nullable=False,
                primary_key=True, default=str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    """
        def __init__(self, **kwargs: Dict) -> None:
            if len(kwargs) == 0:
                self.id = str(uuid4())
                self.date_created = datetime.utcnow()
                self.date_updated = datetime.utcnow()
            else:
                if kwargs.get('id'):
                    self.id = kwargs.get('id', None)
                else:
                    self.id = str(uuid4())
                if kwargs.get('date_created'):
                    self.date_created = datetime.strptime(
                        kwargs.get('date_created', None), BaseModel.DATE_FORMAT)
                else:
                    self.date_created = datetime.utcnow()
                if kwargs.get('date_updated'):
                    self.date_created = datetime.strptime(
                        kwargs.get('date_updated', None), BaseModel.DATE_FORMAT)
                else:
                    self.date_updated = datetime.utcnow()
    """

    def __str__(self) -> str:
        return f"class name: {self.__class__} -> with ID: {self.id}"
