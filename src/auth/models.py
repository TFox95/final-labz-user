from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey, Enum, event
from sqlalchemy.orm import relationship, Mapper, Session
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from core.database import Base


class USER_ROLES(PyEnum):
    ADMIN = 0
    OFFICER = 1
    CONTRACTOR = 2
    CLIENT = 3


class User(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(length=128), index=True)
    email = Column(String(length=128), unique=True, index=True, nullable=False)
    password = Column(String(length=64), nullable=False)
    createdOn = Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False)
    type = Column(Enum(USER_ROLES), nullable=False,
                  default=USER_ROLES.CLIENT.value)
    additional = relationship(
            (lambda: Admin if User.type == USER_ROLES.ADMIN else
                (lambda: Officer if User.type == USER_ROLES.OFFICER else
                    (lambda: Contractor if User.type == USER_ROLES.CONTRACTOR else
                        Client))),
            back_populates="user",
            uselist=False,
            lazy="joined"
        )


class Contractor(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)


class Client(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)
    posted_jobs = relationship("Job", back_populates="clients",
                               uselist=True, lazy="joined")


class Admin(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)
    contractor_roster = relationship("Contractor",
                                     secondary='admin_contractor_association',
                                     back_populates='admins', lazy='dynamic')


class Officer(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)


@event.listens_for(User, "after_insert")
def create_additional(mapper: Mapper, connection: Session, target: User):
    if target.type == USER_ROLES.ADMIN:
        admin = Admin(user=target)
        connection.add(admin)
    elif target.type == USER_ROLES.OFFICER:
        officer = Officer(user=target)
        connection.add(officer)
    elif target.type == USER_ROLES.CONTRACTOR:
        contractor = Contractor(user=target)
        connection.add(contractor)
    elif target.type == USER_ROLES.CLIENT:
        client = Client(user=target)
        connection.add(client)
