from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder as jsonEnc
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.get("/")
async def index() -> JSONResponse:
    content = {"success": "restful-backend connection reached and established",
               "status": status.HTTP_200_OK}
    content = jsonEnc(content)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)
