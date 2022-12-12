import secrets
from typing import List, Optional, Dict, Any

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    SERVICE_NAME: str = "not-defined"

    ENVIRONMENT: str = "production"
    IS_DEV: Optional[bool] = None

    @validator("IS_DEV", pre=True)
    def fill_environment(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, bool):
            return v
        _env = values.get("ENVIRONMENT")
        return _env == "development" or _env == "dev"

    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "Append-ScreeningTale"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    STRIPE_API_KEY_LIVE: str
    STRIPE_WEBHOOK_SECRET: str

    SIMFIN_KEY: str = ""

    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    SECRET_KEY : str
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

    EMAIL_ID: str
    EMAIL_PASS: str

    BASE_URL: str
    FRONTEND_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    FMP_API_BASE: str
    FMP_API_KEY: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return (
            PostgresDsn.build(
                scheme="postgresql",
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
            + f"?application_name={values.get('SERVICE_NAME')}"
        )

    class Config:
        case_sensitive = True


settings = Settings()
