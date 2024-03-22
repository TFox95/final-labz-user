from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import ForeignKey, Enum, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, DBAPIError

from enum import Enum as PyEnum

from core.database import ModelBase as Base, Database


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




#class Transaction(Base):
#    id = Column(Integer, primary_key=True, index=True, nullable=False)
#    amount = Column(String, ForeignKey(Jobs.amount))
#    jobId = Column(Integer, ForeignKey(Jobs.id))
#    job = relationship("Job", backref="transactions")
#    contractor = relationship("Contractor", backref="transactions")
#    transactionDate = Column(DateTime(timezone=True),
#                             server_default=func.now(), nullable=True)


#class Message(Base):
#    id = Column(Integer, primary_key=True, index=True, nullable=False)
#    title = Column(String(length=128), nullable=False)
#    content = Column(String(length=256), nullable=False)
#    sender = Column(Integer, ForeignKey(UserBaseModel.id), nullable=False)
#    recipient = Column(Integer, ForeignKey(UserBaseModel.id), nullable=False)
#   postedOnJob = relationship("Job", back_populates="messages", )


#@event.listens_for(Job, "after_update")
#def update_contractor_jobs(mapper, connection, target: Job):
#    with Database().get_db() as db:  # Acquire session within the listener
#        db: Session = db
#        if target.status == JOB_STATUS_STATES.COMPLETED and target.takenByUser:
#            contractor = target.takenByUser
#            contractor.activeJobs.remove(target)
#            contractor.completedJobs.append(target)
#            db.add(contractor)  # Update contractor in database
#            db.commit()
