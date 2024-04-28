from pydantic import BaseModel
from typing import Optional

from work.emuns import JOB_STATUS_STATES, CATEGORY_STATES


class Post_Job_Schema(BaseModel):
    title: str
    description: str
    status: JOB_STATUS_STATES = JOB_STATUS_STATES.UNASSIGNED
    category: int
    amount: float


class Update_Job_Schema(BaseModel):
    job_id: int
    title: Optional[str]
    description: Optional[str]
    category: Optional[int]
    amount: Optional[float]
