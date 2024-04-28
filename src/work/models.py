from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError

from typing import Optional

from auth.enums import CATEGORY_STATES, JOB_STATUS_STATES
from auth.models import User, Client_Additional, Contractor_Additional
from core.database import ModelBase as Base, Database


class Jobs(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(length=256), index=True, nullable=False)
    description = Column(String(length=512), nullable=False)
    category = Column(Enum(CATEGORY_STATES), nullable=False)
    poster = relationship("Client_Additional", back_populates="posted_jobs")
    poster_id = Column(Integer, ForeignKey(Client_Additional.id))
    taken_by_user_id = Column(Integer, ForeignKey(Contractor_Additional.id))
    taken_by_user = relationship("Contractor_Additional",
                                 back_populates="jobs")
    amount = Column(Float, nullable=False)
    status = Column(Enum(JOB_STATUS_STATES), nullable=False,
                    default=JOB_STATUS_STATES.UNASSIGNED.value)
    # messages = relationship("Message", back_populates="job",
    #                        lazy="joined", uselist=True)

    def __init__(self, title: str, description: str, category: CATEGORY_STATES,
                 amount: float, status: JOB_STATUS_STATES, poster: User):
        self.title = title
        self.description = description
        self.category = category
        self.amount = amount
        self.poster = poster
        self.status = status

    def create(self, db: Database) -> int:
        with db.get_db() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self.id

    def update(self, db: Database, fields: dict) -> Optional[str]:
        with db.get_db() as session:

            for field, value in fields.items():
                setattr(self, field, value) if (
                    field != "category"
                ) else setattr(self, field, CATEGORY_STATES(value).name)
            try:
                session.merge(self)
                session.commit()
            except SQLAlchemyError as exc:
                print(str(exc))
                return None
        return "Job was successfully updated."

    def get_by_id(db: Database, job_id: int):
        with db.get_db() as session:
            stored_obj: Jobs = session.query(
                Jobs).filter_by(id=job_id).scalar()
            return stored_obj

    def get_jobs_by_userId(db: Database, user_additional_id: int):
        with db.get_db() as session:
            return session.query(Jobs).filter_by(
                poster_id=user_additional_id).all()

    def assign_contractor(self, db: Database, contractor) -> bool or str:
        """Assigns a contractor to this job and updates the database.

        Args:
            contractor: The User object representing the contractor.

        Returns:
            True on success, a descriptive error string on failure.
        """

        try:
            with db.get_db() as session:
                self.takenByUser = contractor
                session.merge(self)
                session.commit()
                return True
        except IntegrityError as e:
            # Handle potential constraint violations, foreign key errors, etc.
            session.rollback()
            return f"Error assigning contractor: {str(e)}, Integrity constraint violated."
        except (DBAPIError, Exception) as e:
            # Handle other database or unexpected errors
            session.rollback()
            return f"Error assigning contractor: {str(e)}"


# class Transaction(Base):
#    id = Column(Integer, primary_key=True, index=True, nullable=False)
#    #amount = Column(String, ForeignKey(Jobs.amount))
#    job_id = Column(Integer, ForeignKey(Jobs.id))
#    job = relationship(Jobs, backref="transactions")
#    contractor = relationship(Contractor_Additional, backref="transactions")
#    contractor_id = relationship(Integer,
#                                 ForeignKey(Contractor_Additional.id))
#    transactionDate = Column(DateTime(timezone=True),
#                             server_default=func.now(), nullable=True)


# class Message(Base):
#    id = Column(Integer, primary_key=True, index=True, nullable=False)
#    title = Column(String(length=128), nullable=False)
#    content = Column(String(length=256), nullable=False)
#    sender = Column(Integer, ForeignKey(User.id), nullable=False)
#    recipient = Column(Integer, ForeignKey(User.id), nullable=False)
#    job = relationship(Jobs, back_populates="messages",
#                       lazy="select", uselist=False)
#    job_id = Column(Integer, ForeignKey(Jobs.id, ondelete="CASCADE"))
