from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder as Json_Enc

from pydantic import BaseModel as Base

from random import randint

NAMESPACE = "Auth Routes"


class login(Base):
    email: str
    password: str


router = APIRouter(
    prefix="/user",
    tags=["user"]
)
# Any Routes Defined at this point and Below are
# just Dummy Routes they will be replaced


@router.get("/")
def get_auth():
    return "auth app created!"


@router.get("/{user_id}")
async def get_user(user_id: str, login_info: login) -> JSONResponse:
    if not user_id.isnumeric():
        errorMessage = {
            "message": "User ID must be integer",
            "status": f"{status.HTTP_404_NOT_FOUND}"
        }
        raise HTTPException(detail=errorMessage,
                            status_code=status.HTTP_409_CONFLICT)

    content = {
        "data": {
            "id": user_id,
            "name": "John Doe",
            "email": login_info.email,
            "type": str(randint(0, 5)),
            "additional": {
                "user_id": user_id,
                "posted_jobs": [

                ]
            }
        }
    }

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.get("s")
async def get_all_users():
    content = []

    for n in range(169):
        user_id = str(randint(0, 1000000))

        content.append({
            "id": user_id,
            "name": "John Doe",
            "email": f"{str(randint(0, 40300))}@email.com",
            "type": str(randint(0, 5)),
            "additional": {
                "user_id": user_id,
                "posted_jobs": [

                ]
            }
        })

    content = Json_Enc(content)
    return JSONResponse(content={"users": content}, status_code=status.HTTP_200_OK)
