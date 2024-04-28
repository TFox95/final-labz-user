from fastapi import (Request, HTTPException,
                     status, Depends,
                     Cookie)
from typing import Optional

from core.database import database
from auth.models import User
from auth.crud import TokenHandler
from auth.schemas import Decoded_Token


def check_refresh(Authorization: Optional[str] = Cookie(None)
                  ) -> Decoded_Token:
    try:
        return TokenHandler.decode_token(Authorization)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "401",
                "message": f"{exc}; Please Sign back-in"
            }
        )


# In Testing
# Middleware function to validate tokens and check user ID and email
async def validate_tokens(request: Request):  # , next):
    access: Optional[str] = request.headers.get("Authorization").split(" ")[1]
    refresh: Optional[str] = request.cookies.get("Authorization")

    # Check if tokens exist
    if not access or not refresh:
        raise next(request, refresh)

    decoded_Access = TokenHandler.decode_token(access)
    decoded_Refresh = TokenHandler.decode_token(refresh)

    if decoded_Access.user_id != decoded_Refresh.user_id:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail="detail")

    return await next(request)


async def check_auth(request: Request,
                     Authorization: Optional[str] = Cookie(None)
                     ) -> Decoded_Token:
    """
    Check if Authorization header is present and return the
    Authorization token if it is. Otherwise, raise an HTTPException.

    Args:
        request (Request): The request to check for the Authorization header.
        Authorization (str, optional): The Authorization cookie to use
        for token validation.
            Defaults to None.

    Returns:
        str: The Authorization token as a string.

    Raises:
        HTTPException: If no Authorization header is found
        or if the token is invalid.
    """
    try:
        refresh = TokenHandler.decode_token(Authorization)
        if refresh.token_type.lower() == "refresh":
            # user: User = User.get_by_id(database, refresh.user_id)
            # if user.if_user_is_active():
            pass
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "401",
                "message": f"{exc}; Please Sign back-in"
            }
        )
    finally:
        try:
            AccessToken = request.headers["Authorization"].split(" ")[1]
            DecodedAccess = TokenHandler.decode_token(AccessToken)
            if DecodedAccess.user_id == refresh.user_id:
                return DecodedAccess
            raise ValueError("Please Try again later")

        except Exception as exc:

            raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail={
                    "status": "418",
                    "message": str(exc)
                }
            )


async def get_current_user(token: Decoded_Token = Depends(check_auth)
                           ) -> User:
    try:
        DecodedUser: User = User.get_by_id(database, token.user_id)
        if DecodedUser.if_user_is_active():
            return DecodedUser

    except Exception as exc:
        print(str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "500",
                "message": "Error retrieving User; Please try again later."
            }
        )


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.type.name.lower() != "admin":
        content = {
            "status": "500",
            "message": "Sorry something went wrong; Try again later"
        }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=content)
    return user
