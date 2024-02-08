from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey, Enum, event
from sqlalchemy.orm import relationship, Mapper, Session
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from argon2 import PasswordHasher
from enum import Enum as PyEnum

from pydantic import EmailStr
from typing import Optional

from core.database import Base, Database
from core.config import settings


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
            (lambda: Contractor if User.type == USER_ROLES.CONTRACTOR else
                (lambda: Officer if User.type == USER_ROLES.OFFICER else
                    (lambda: Admin if User.type == USER_ROLES.ADMIN else
                        Client))),
            back_populates="users",
            uselist=False,
            lazy="joined"
        )

    def set_password(self, password: str):
        ph = PasswordHasher()
        self.password = ph.hash(password, settings.PASSWORD_SALT_KEY)

    def verify_password(self, password: str) -> bool:
        ph = PasswordHasher()
        password = ph.hash(password, settings.PASSWORD_SALT_KEY)
        return ph.verify(self.password, password)

    def create(self):
        """
        Adds the user object to the database and commits the changes.

        Returns:
            User: The saved user object with its assigned ID.
        """

        with self.db.get_db() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self

    def update(self, fields: dict):
        """
        Updates the user object in the database with the provided fields.

        Args:
            fields (dict): A dictionary containing the fields to update
            and their new values.

        Returns:
            User: The updated user object.
        """
        with self.db.get_db() as session:
            for field, value in fields.items():
                setattr(self, field, value)
            session.merge(self)
            session.commit()
            session.refresh(self)
            return self

    def get_by_id(self, user_id: int):
        """
        Retrieves a user object by their user Id.

        Args:
            user_id (int): The Id number of the user to retrieve.

        Returns:
            User | None: The user object if found, None otherwise.
        """

        with self.db.get_db() as session:
            stored_obj: self = session.query(self).filter_by(id=user_id).first()
            return stored_obj

    def get_by_email(self, email: EmailStr):
        """
        Retrieves a user object by their email address.

        Args:
            email (EmailStr): The email address of the user to retrieve.

        Returns:
            User | None: The user object if found, None otherwise.
        """

        with self.db.get_db() as session:
            stored_obj: self = session.query(self).filter_by(email=email).first()
            return stored_obj

    def has_type(self, type: USER_ROLES) -> bool:
        """
        Checks if the user has the specified role.

        Args:
            type (USER_ROLES): The role to check for.

        Returns:
            bool: True if the user has the specified role, False otherwise.
        """

        if self.type != type:
            return False
        return True

    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Changes the user's password.

        Args:
            old_password (str): The current password of the user.
            new_password (str): The new password to set for the user.

        Returns:
            bool: True if the password was changed, False otherwise.
        """

        if not self.verify_password(old_password):
            return False

        with self.db.get_db() as session:
            session.merge(self)
            session.commit()
            session.refresh(self)
        return True

    def __init__(self, name: str, email: str, password: str, db: Database,
                 type: Optional[USER_ROLES] = USER_ROLES.CLIENT):
        self.name = name
        self.email = email
        self.set_password(password)
        self.type = type
        self.db = db


class Contractor(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)
    activeJobs = relationship("Job", back_populates="contractors",
                              uselist=True, lazy="joined")
    completedJobs = relationship("Job", back_populates="contractors",
                                 uselist=True, lazy="joined")


class Client(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="additional", uselist=False)
    postedJobs = relationship("Job", back_populates="clients",
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
