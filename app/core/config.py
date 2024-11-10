import os
import warnings
from typing import Annotated, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: list[str] | str) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    SERVICE_NAME: str = ""
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis"
    AUTH_URL: str = "http://127.0.0.1:5000/api/v1/me"
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BASE_DIR: str = str(os.path.dirname(os.path.dirname(__file__)))
    LOG_DIR: str = str(os.path.join(BASE_DIR, "logs"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    PROJECT_NAME: str = "FastAPI Template"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_template"
    POSTGRES_SCHEMA: str = "public"
    POSTGRES_ENCRYPTION_KEY: str = "changethis"
    POSTGRES_ENCRYPTION_KEY_VERSION: int = 1

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value in ["changethis", "admin", "root", "postgres"]:
            message = (
                f'The value of {var_name} is "{value}", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("POSTGRES_ENCRYPTION_KEY", self.POSTGRES_ENCRYPTION_KEY)

        return self


settings = Settings()
