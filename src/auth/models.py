from sqlalchemy import  Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from core.database import Base


class UserRoles(PyEnum):
    ADMIN = 0
    OFFICER = 1
    CONTRACTOR = 2
    CLIENT = 3


class User(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(length=100), index=True)
    email = Column(String(length=125), unique=True, index=True, nullable=False)
    password = Column(String(length=255), nullable=False)
    role = Column(Enum(UserRoles), nullable=False, default=UserRoles.CLIENT)
    additional = relationship()


class Contractor(User):
    pass
