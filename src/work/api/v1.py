from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from auth.middleware import check_auth, get_current_user
from auth.models import User
from work.models import Jobs
from work.emuns import JOB_STATUS_STATES, CATEGORY_STATES
from work.schemas import Post_Job_Schema, Update_Job_Schema
from core.config import JsonRender
from core.database import database

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    dependencies=[Depends(check_auth)]

)


# Get Routes defined below:
@router.get("/", response_class=JsonRender,
            status_code=status.HTTP_200_OK)
async def check_router():
    return "Bookings reached"


@router.get("/retrieve_jobs", response_class=JsonRender,
            status_code=status.HTTP_200_OK)
async def retrieve_user_jobs(user: User = Depends(get_current_user)):
    jobs = Jobs.get_jobs_by_userId(database, user.additional.id)
    return jobs


@router.get("/retrieve_job/{job_id}", response_class=JsonRender,
            status_code=status.HTTP_200_OK)
async def retrieve_select_job(job_id: int,
                              user: User = Depends(get_current_user)
                              ) -> JSONResponse:
    job = Jobs.get_by_id(database, job_id)
    return job


# POST Routes defined below:
@router.post("/post_job", response_class=JsonRender,
             status_code=status.HTTP_200_OK)
async def user_job_post(json: Post_Job_Schema,
                        decoded: User = Depends(get_current_user)
                        ) -> JSONResponse:

    job = Jobs(title=json.title, description=json.description,
               status=json.status.name,
               category=CATEGORY_STATES(json.category).name,
               amount=json.amount, poster=decoded.additional)
    job.create(database)

    content = {
        "status": "200",
        "message": "Task was successfully created and added to the task pool"
    }
    return content


@router.post("/assign_contractor", response_class=JsonRender,
             status_code=status.HTTP_200_OK)
async def assign_contractor_to_job():
    pass


# PUT Routes defined below:
@router.put("/update_job", response_class=JsonRender,
            status_code=status.HTTP_200_OK)
async def update_user_post(json: Update_Job_Schema,
                           decoded: User = Depends(get_current_user),
                           ) -> JSONResponse:

    job = Jobs.get_by_id(database, json.job_id)

    if (job.poster_id != decoded.additional.id) or (
            decoded.type.name.lower() != "admin" and (
            job.poster_id != decoded.additional.id)):

        content = {
            "status": 404,
            "message": "Job doesn't exist; please check again later."
        }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=content)

    result = job.update(database, json.dict(exclude_unset=True))
    return result


# DELETE Routes defined below:
@router.delete("/remove_job", response_class=JsonRender,
               status_code=status.HTTP_200_OK)
async def remove_job_post():
    pass
