from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import ForeignKey, Enum, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, DBAPIError

from enum import Enum as PyEnum

from core.database import Base, Database
from auth.models import User


class CATEGORY_STATES(PyEnum):
    PC_CUSTOM_BUILD = 0
    SOFTWARE_INSTALL = 1
    SECURITY_HARDWARE_INSTALL = 2
    SERVER_SETUP = 3
    OTHER = 4


class JOB_STATUS_STATES(PyEnum):
    UNASSIGNED = 0
    ASSIGNED = 1
    IN_PROGRESS = 2
    PENDING = 3
    COMPLETED = 4
    CANCELLED = 5


class Job(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(length=256), index=True, nullable=False)
    description = Column(String(length=512), nullable=False)
    category = Column(Enum(CATEGORY_STATES), nullable=False)
    poster = relationship(User, back_populates="PostedJobs",
                          lazy="joined")
    takenByUser = relationship(User, back_populates="acitveJobs")
    creationDate = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(JOB_STATUS_STATES), nullable=False,
                    default=JOB_STATUS_STATES.UNASSIGNED.value)
    messages = relationship("Message", back_populates="jobs",
                            lazy="joined", uselist=True)

    def __init__(self, title: str, description: str, category: CATEGORY_STATES,
                 amount: float, creator: User, db: Database):
        self.title = title
        self.description = description
        self.category = category
        self.amount = amount
        self.poster = creator
        self.db = db

    def create(self) -> int:
        with self.db.get_db() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self.id

    def update(self, fields: dict):
        with self.db.get_db() as session:
            for field, value in fields.items():
                setattr(self, field, value)
            session.merge(self)
            session.commit()
            session.refresh(self)
            return self

    def get_by_id(self, job_id: int):
        with self.db.get_db() as session:
            stored_obj: self = session.query(self).filter_by(id=job_id).first()
            return stored_obj

    def assign_contractor(self, contractor: User) -> bool | str:
        """Assigns a contractor to this job and updates the database.

        Args:
            contractor: The User object representing the contractor.

        Returns:
            True on success, a descriptive error string on failure.
        """

        try:
            with self.db.get_db() as session:
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


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    amount = Column(String, ForeignKey("Job.amount"))
    jobId = Column(Integer, ForeignKey("Job.id"))
    recipient = Column(String, ForeignKey("Job.takenByUser.name"))
    paidBy = Column(String, ForeignKey("Job.poster.name"))
    transactionDate = Column(DateTime(timezone=True),
                             server_default=func.now(), nullable=True)


class Message(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(length=128), nullable=False)
    content = Column(String(length=256), nullable=False)
    sender = Column(Integer, ForeignKey(User.id), nullable=False)
    recipient = Column(Integer, ForeignKey(User.id), nullable=False)
    postedOnJob = relationship("Job", back_populates="messages", )


@event.listens_for(Job, "after_update")
def update_contractor_jobs(mapper, connection, target: Job):
    with Database().get_db() as db:  # Acquire session within the listener
        db: Session = db
        if target.status == JOB_STATUS_STATES.COMPLETED and target.takenByUser:
            contractor = target.takenByUser
            contractor.activeJobs.remove(target)
            contractor.completedJobs.append(target)
            db.add(contractor)  # Update contractor in database
            db.commit()
