from pydantic import EmailStr
from datetime import datetime
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from auth.models import (User, Admin_Additional, Client_Additional,
                         Contractor_Additional)
from work.models import Jobs
from core.database import BaseSchema as Base


# Generate Pydantic schemas
JobDataSchema = sqlalchemy_to_pydantic(Jobs)

sql_contractor_data = sqlalchemy_to_pydantic(Contractor_Additional)
sql_admin_data = sqlalchemy_to_pydantic(Admin_Additional)
sql_client_data = sqlalchemy_to_pydantic(Client_Additional)

sql_user = sqlalchemy_to_pydantic(User)


# Include nested schemas
class Additional_Contractor_Schema(sql_contractor_data):
    jobs: list[JobDataSchema] or None = None


class ContractorSchema(sql_user):
    additional: Additional_Contractor_Schema or None = None


class Additional_Client_Schema(sql_client_data):
    posted_jobs: JobDataSchema or None = None


class ClientSchema(sql_user):
    additional: Additional_Client_Schema or None = None


class Additional_Admin_Schema(sql_admin_data):
    contractor_roster: list[ContractorSchema] or None = None


class AdminSchema(sql_user):
    additional: Additional_Admin_Schema or None = None


class Decoded_Token(Base):
    iss: str
    exp: datetime
    iat: datetime
    user_id: int
    token_type: str


class Encoded_Token(Base):
    token: str


class Register_User(Base):
    name: str or None
    email: EmailStr or None
    password: str or None
    type: int or None


class Update_User_Parameters(Base):
    email: EmailStr or None = None
    name: str or None = None
    password: str or None = None


class Register_User_Payload(Base):
    status: str
    message: str


class Login_User(Base):
    email: EmailStr or None
    password: str or None


class Login_User_Payload(Base):
    token: Encoded_Token
    user: str


# def admin_to_schema(admin: Admins) -> Admins_Schema:
#    data = admin.dict()
#    if data.get('additional_data'):
#        data['additional_data'] = Linked_Admin_Data(
#            **data['additional_data'].dict()
#        )
#    return Admins_Schema(**data)
