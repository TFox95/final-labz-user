from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel as Base
from typing import ContextManager

from core.config import settings


class Database:
    def __init__(self):
        self.engine = create_engine(str(settings.DATABASE_URI),
                                    pool_pre_ping=True, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False, bind=self.engine)

    def get_db(self) -> Session:
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()


class BaseSchema(Base):
    """
    Base Class for all Sqlalchemy Model Schema's
    """
    class Config:
        orm_mode = True
        # from_attributes = True


@as_declarative()
class ModelBase:
    """
    Base class for all SQLAlchemy models in this application.

    This class provides the following features:

    * Automatic table name generation based
        on the class name (lowercase with an 's' suffix).

    * Standardized metadata management using a shared DeclarativeMeta class.

    Do not instantiate this class directly; use child classes instead.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generates the table name for a child class based on its name.

        Returns:
            str: The table name with lowercase name and 's' suffix.
        """
        return f"{cls.__name__.lower()}"

    def dict(self, exclude_none=True):
        return {
            key: value
            for key, value in self.__dict__.items()
            if value is not None and key not in ('_sa_instance_state')
        }

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_sa_instance_state']
        # del state['password']  # Exclude password for safety
        return state


database = Database()
