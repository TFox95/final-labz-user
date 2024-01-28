from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy import ForeignKey, Enum, event
from sqlalchemy.orm import relationship, Mapper, Session
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from core.database import Base


class UserRoles(PyEnum):
    ADMIN = 0
    OFFICER = 1
    CONTRACTOR = 2
    CLIENT = 3


class User(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(length=128), index=True)
    email = Column(String(length=128), unique=True, index=True, nullable=False)
    password = Column(String(length=64), nullable=False)
    date_joined = Column(DateTime(timezone=True),
                         server_default=func.now(),
                         nullable=False)
    bio = Column(Text(length=256), default="")
    role = Column(Enum(UserRoles), nullable=False, default=UserRoles.CLIENT)
    additional = relationship("Admin" if role == UserRoles.ADMIN else
                              "Officer" if role == UserRoles.OFFICER else
                              "Contractor" if role == UserRoles.CONTRACTOR else
                              "Client", back_populates="users", uselist=False,
                              lazy="joined")


class Contractor(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)



