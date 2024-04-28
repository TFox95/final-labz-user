from pydantic import BaseModel

from typing import Optional


class job_form_schema(BaseModel):
    firstName: str
    lastName: str
    companyName: Optional[str]
    bussinessEmail: Optional[str]
    phoneNumber: str
    description: str
