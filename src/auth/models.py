from fastapi import HTTPException, status
from sqlalchemy import (ForeignKey,
                        Column, Integer,
                        String, Enum)
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from pydantic import EmailStr

from argon2 import PasswordHasher
from argon2.exceptions import (VerifyMismatchError,
                               InvalidHashError, VerificationError)
from os import urandom

from auth.enums import USER_ROLES
from core.database import ModelBase as Base, Database


class User(Base):

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(length=128), index=True)
    email = Column(String(length=128), unique=True, index=True, nullable=False)
    password = Column(String(length=128), nullable=False)
    created_on = Column(DateTime(timezone=True), server_default=func.now(),
                        nullable=False)
    type = Column(Enum(USER_ROLES), nullable=False)

    # Define a polymorphic relationship
    additional = relationship("Additional", uselist=False, lazy="joined")

    def __init__(self, name: str = None, email: str = None,
                 password: str = None, type=USER_ROLES.CLIENT):
        self.name = name
        self.email = email
        self.set_password(password)
        self.type = type

    def set_password(self, password: str):
        if password:
            ph = PasswordHasher(salt_len=16)
            self.password = ph.hash(password=password, salt=urandom(16))

    def verify_password(self, password: str) -> bool:
        ph = PasswordHasher()
        try:
            return ph.verify(hash=self.password, password=password)
        except (VerifyMismatchError,
                InvalidHashError,
                VerificationError) as exc:
            print(str(exc))
            return False

    def change_password(self, db: Database,
                        old_password: str, new_password: str) -> bool:
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

        with db.get_db() as session:
            self.set_password(new_password)
            session.merge(self)
            session.commit()
        return True

    def create(self, db: Database):
        """
        Adds the user object to the database and commits the changes.

        Returns:
            User: The saved user object with its assigned ID.
        """

        if self.if_email_exists(db=db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "400", "message": "email Already Exists"
                })

        if self.type == USER_ROLES.CLIENT:
            self.additional = Client_Additional()
        elif self.type == USER_ROLES.CONTRACTOR:
            self.additional = Contractor_Additional()
        elif self.type == USER_ROLES.ADMIN:
            self.additional = Admin_Additional()
        elif self.type == USER_ROLES.OFFICER:
            self.additional = Officer_Additional()

        with db.get_db() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
        return True

    def update(self, db: Database, fields: dict):
        """
        Updates the user object in the database with the provided fields.

        Args:
            fields (dict): A dictionary containing the fields to update
            and their new values.

        Returns:
            User: The updated user object.
        """

        for field, value in fields.items():
            setattr(self, field, value) if (
                field != "password") else self.set_password(value)

        with db.get_db() as session:
            session.merge(self)
            session.commit()
            return self

    def archive_user(self, db: Database):
        self.type = USER_ROLES.INACTIVE

        with db.get_db() as session:
            session.merge(self)
            session.commit()
            return self

    def remove_user(self, db: Database):
        self.type = USER_ROLES.REMOVED

        with db.get_db() as session:
            session.merge(self)
            session.commit()
            return self

    def restore_user(self, db: Database):
        self.type = self.additional.type

        with db.get_db() as session:
            session.merge(self)
            session.commit()
            return self

    def get_by_id(db: Database, user_id: int):
        """
        Retrieves a user object by their user Id.

        Args:
            user_id (int): The Id number of the user to retrieve.

        Returns:
            User | None: The user object if found, None otherwise.
        """

        with db.get_db() as session:
            user = session.query(User).filter_by(
                id=user_id).scalar()
            user_type = user.type if user else None

            if not user_type:
                return None

            if user_type == USER_ROLES.CONTRACTOR:
                return session.query(User).join(Additional).filter(
                    User.id == user_id, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Contractor_Additional))).scalar()

            elif user_type == USER_ROLES.CLIENT:
                return session.query(User).join(Additional).filter(
                    User.id == user_id, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Client_Additional))).scalar()

            elif user_type == USER_ROLES.ADMIN:
                return session.query(User).join(Additional).filter(
                    User.id == user_id, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Admin_Additional))).scalar()

            elif user_type == USER_ROLES.OFFICER:
                return session.query(User).join(Additional).filter(
                    User.id == user_id, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Officer_Additional))).scalar()

    def get_by_email(db: Database, email: EmailStr):
        """
        Retrieves a user object by their email address.

        Args:
            email (EmailStr): The email address of the user to retrieve.

        Returns:
            User | None: The user object if found, None otherwise.
        """

        with db.get_db() as session:

            user = session.query(User).filter_by(
                email=email).scalar()
            user_type = user.type if user else None

            if not user_type:
                return None

            if user_type == USER_ROLES.CONTRACTOR:
                return session.query(User).join(Additional).filter(
                    User.email == email, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Contractor_Additional))).scalar()
            elif user_type == USER_ROLES.CLIENT:
                return session.query(User).join(Additional).filter(
                    User.email == email, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Client_Additional))).scalar()

            elif user_type == USER_ROLES.ADMIN:
                return session.query(User).join(Additional).filter(
                    User.email == email, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Admin_Additional))).scalar()

            elif user_type == USER_ROLES.OFFICER:
                return session.query(User).join(Additional).filter(
                    User.email == email, Additional.type == user_type).options(
                    joinedload(User.additional.of_type(
                        Officer_Additional))).scalar()

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

    def if_user_is_active(self) -> bool:
        if (self.type == USER_ROLES.REMOVED) or (
                self.type == USER_ROLES.INACTIVE):
            raise ValueError("Something went wrong")
        return True

    def if_email_exists(self, db: Database):
        result = db.get_db().query(User).filter_by(email=self.email).scalar()
        if not result:
            return False
        return True


class Additional(Base):

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship("User", back_populates="additional",
                        uselist=False)
    type = Column(Enum(USER_ROLES), nullable=False)

    # Define polymorphic identity
    __mapper_args__ = {
        'polymorphic_identity': 'Additional',
        'polymorphic_on': type
    }


class Admin_Additional(Additional):

    id = Column(Integer, ForeignKey(Additional.id, ondelete="CASCADE"),
                primary_key=True, index=True, nullable=False)
    # Add role-specific columns for Admin
    # contractor_roster = relationship(User, uselist=True, lazy="dynamic")

    __mapper_args__ = {
        'polymorphic_identity': USER_ROLES.ADMIN
    }


class Officer_Additional(Additional):

    id = Column(Integer, ForeignKey(Additional.id, ondelete="CASCADE"),
                primary_key=True, index=True, nullable=False)
    # Add role-specific columns for Officer

    __mapper_args__ = {
        'polymorphic_identity': USER_ROLES.OFFICER
    }


class Contractor_Additional(Additional):

    id = Column(Integer, ForeignKey(Additional.id, ondelete="CASCADE"),
                primary_key=True, index=True, nullable=False)
    # Add role-specific columns for Contractor
    jobs = relationship("Jobs", back_populates="taken_by_user",
                        lazy="joined", uselist=True)

    __mapper_args__ = {
        'polymorphic_identity': USER_ROLES.CONTRACTOR
    }


class Client_Additional(Additional):

    id = Column(Integer, ForeignKey(Additional.id, ondelete="CASCADE"),
                primary_key=True, index=True, nullable=False)
    posted_jobs = relationship("Jobs", back_populates="poster",
                               lazy="joined", uselist=True)

    __mapper_args__ = {
        'polymorphic_identity': USER_ROLES.CLIENT
    }
