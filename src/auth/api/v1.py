from fastapi import APIRouter, HTTPException, status, Depends, Cookie, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from typing import Optional

from core.config import JsonRender
from core.database import database

from auth.models import User
from auth.crud import TokenHandler, check_password_strength
from auth.enums import USER_ROLES
from auth.middleware import (get_current_user, check_auth,
                             get_current_admin)
from auth.schemas import (Register_User, Login_User,
                          Update_User_Parameters)

NAMESPACE = "Auth Routes"

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[]
)


# Post Routes Defined Below
@router.post("/register",
             response_class=JsonRender,
             status_code=status.HTTP_200_OK)
async def register(json: Register_User) -> JSONResponse:

    try:
        check_password_strength(json.password)
        user = User(json.name, json.email,
                    json.password, USER_ROLES(json.type))
        user.create(database)

        content = {
            "status": 200,
            "message": f"user, {user.name}, was created successfully"
        }
        return content

    except Exception as exc:
        raise exc


@router.post("/login",
             response_class=JsonRender,
             status_code=status.HTTP_200_OK)
async def login(json: Login_User, res: JsonRender) -> JSONResponse:

    user: User = User.get_by_email(db=database, email=json.email)
    if (not user) or (
        json.email != user.email) or (
            not user.verify_password(json.password) or (
                user.type.name == "REMOVED") or (
                    user.type.name == "INACTIVE")):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "404",
                "message": "Not found; Please check email and password"
            }
        )

    AccessToken = TokenHandler.encode_token(user_id=user.id,
                                            token_type="Access")
    RefreshToken = TokenHandler.encode_token(user_id=user.id,
                                             token_type="Refresh")
    res.headers["Authorization"] = f"Bearer {AccessToken.token}"

    expires_at = 60 * 60 * 24 * 14
    max_age = datetime.utcnow() + timedelta(days=14)

    res.set_cookie(key="Authorization", value=RefreshToken.token,
                   httponly=True, secure=True, expires=expires_at,
                   max_age=max_age)
    content = jsonable_encoder(user, exclude=["password", "id"])
    content["additional"].pop("user_id")
    content["additional"].pop("id")
    return content


# Get Routes Defined Below.
@router.get("/",
            response_class=JsonRender,
            status_code=status.HTTP_200_OK)
def get_auth():
    user = User.get_by_email(database, "client@client.com")
    return user


@router.get("/token",
            response_class=JsonRender,
            status_code=status.HTTP_200_OK)
async def token_refresh(req: Request, res: JsonRender,
                        Authorization: Optional[str] = Cookie(None)
                        ) -> JSONResponse:
    DecodedRefresh = TokenHandler.decode_token(Authorization)
    NewAccess = TokenHandler.encode_token(DecodedRefresh.user_id,
                                          "Access")
    NewRefresh = TokenHandler.encode_token(DecodedRefresh.user_id,
                                           "Refresh")

    expires_at = 60 * 60 * 24 * 14
    max_age = datetime.utcnow() + timedelta(days=14)

    res.headers["Authorization"] = f"Bearer {NewAccess.token}"
    res.set_cookie(key="Authorization", value=NewRefresh.token, httponly=True,
                   secure=True, expires=expires_at, max_age=max_age)
    content = {
        "status": "200",
        "message": "Auth tokens refreshed successfully"
    }
    return content


@router.get("/retrieve_user",
            response_class=JsonRender,
            dependencies=[Depends(check_auth)],
            status_code=status.HTTP_200_OK)
async def get_user(user: User = Depends(get_current_user)
                   ) -> JSONResponse:
    if not user:
        errorMessage = {
            "message": "User ID must be integer",
            "status": status.HTTP_404_NOT_FOUND.__str__
        }
        raise HTTPException(detail=errorMessage,
                            status_code=status.HTTP_404_NOT_FOUND)

    content = jsonable_encoder(user, exclude=["password", "id"])
    content["additional"].pop("user_id")
    content["additional"].pop("id")
    return content


@router.get("/retrieve_user/{targ_user_id}",
            response_class=JsonRender,
            dependencies=[Depends(check_auth)],
            status_code=status.HTTP_200_OK)
async def get_specific_user(targ_user_id: str,
                            decoded: User = Depends(get_current_user)
                            ) -> JSONResponse:
    content = None
    if not targ_user_id.isnumeric():
        content = {
            "status": "400",
            "message": "Parameter must be an interger"
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=content)

    targ_user: User = User.get_by_id(database, int(targ_user_id))

    if not targ_user or (
            decoded.type.name != "ADMIN" and targ_user.type.name == "ADMIN"):
        content = {
            "status": "404",
            "message": "User not Found"
        }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=content)

    if decoded.type.name == "ADMIN":
        content = jsonable_encoder(targ_user)
    elif decoded.type.name != "ADMIN":
        content = jsonable_encoder(targ_user, exclude=["id", "password"])
        content["additional"].pop("id")
        content["additional"].pop("user_id")

    return content


@router.get("/retrieve_users",
            response_class=JsonRender,
            dependencies=[Depends(get_current_admin)],
            status_code=status.HTTP_200_OK)
async def get_users() -> JSONResponse:
    content = {
        "status": "200",
        "users":  database.get_db().query(User).all()
    }

    content = jsonable_encoder(content)
    return content


@router.get("/retrieve_users/{group}", response_class=JsonRender,
            dependencies=[Depends(get_current_admin)],
            status_code=status.HTTP_200_OK)
async def get_users_by_group(group: int):

    try:
        content = {
            "status": "200",
            "users": database.get_db().query(User).filter_by(type=group).all()
        }
        return content

    except Exception as exc:
        print(str(exc))
        raise HTTPException(detail={
            "status": "500",
            "message": "Sorry something went wrong; Try again later"
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Put routes Defined Below
@router.put("/update_user",
            response_class=JsonRender,
            dependencies=[Depends(check_auth)],
            status_code=status.HTTP_200_OK)
async def update_user_parameters(data: Update_User_Parameters,
                                 decoded: User = Depends(get_current_user)
                                 ) -> JSONResponse:
    decoded.update(database, data.dict(exclude_unset=True))
    content = jsonable_encoder(decoded, exclude=["password", "id"])
    content["additional"].pop("id")
    content["additional"].pop("user_id")
    return content


# Delete Routes Defined Below
@router.delete("/retrieve_user/remove",
               response_class=JsonRender,
               dependencies=[Depends(check_auth)],
               status_code=status.HTTP_200_OK)
async def remove_user(decoded: User = Depends(get_current_user)):
    pass
