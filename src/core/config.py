
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, validator, BaseSettings

from fastapi.responses import JSONResponse


class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str,
                              List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    JWT_SECRET_KEY: str

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[
                               str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


class JsonRender(JSONResponse):
    """
    This Class was created to return certain content that would
    allow content that needs to be return as an object to utilize
    the reponse_model argument on an API Endpoint but it keeps
    consistency of the Apps Json-scheme.
    """

    def render(self, content: any) -> bytes:
        # Here you can modify the response content or headers as needed
        return super().render({'data': content})


settings = Settings()
