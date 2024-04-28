from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings, JsonRender
from auth.api import v1 as auth
from work.api import v1 as work
from emailManager.api import v1 as mail


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(
            origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return _app


app = get_application()
# ModelBase.metadata.create_all(database.engine)


@app.get("/", response_class=JsonRender, status_code=status.HTTP_200_OK)
async def index() -> JSONResponse:

    content = {
        "status": "200",
        "message": "Connection to database has been established"
    }
    return content

app.include_router(auth.router)
app.include_router(work.router)
app.include_router(mail.router)
