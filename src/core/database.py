from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker, Session
from typing import ContextManager

from core.config import settings


class Database:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URI,
                                    pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False, bind=self.engine)

    def get_db(self) -> ContextManager[Session]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models in this application.

    This class provides the following features:

    * Automatic table name generation based on the class name (lowercase with an 's' suffix).
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
        return f"{cls.__name__.lower()}s"


database = Database()
