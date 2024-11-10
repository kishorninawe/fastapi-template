import logging

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.SERVICE_NAME}/docs/openapi.json",
    docs_url=f"{settings.SERVICE_NAME}/docs",
)


def get_custom_error_message(err):
    if err["loc"][0] in ["query", "path"]:
        if err["type"] == "missing":
            return f"{err['loc'][1].replace('_', ' ').capitalize()} is required"
        elif err["type"] == "string_pattern_mismatch":
            return f"Please enter a valid {err['loc'][1].replace('_', ' ')}"
        elif err["type"] == "greater_than":
            return f"{err['loc'][1].replace('_', ' ').capitalize()} should be greater than {err.get('input')}"
        elif err["type"] == "less_than":
            return f"{err['loc'][1].replace('_', ' ').capitalize()} should be less than {err.get('input')}"
        elif err["type"] == "uuid_parsing":
            return f"Invalid {err['loc'][1].replace('_', ' ')}!"
        else:
            return err["msg"]
    else:
        return err["msg"]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        content={
            "detail": {
                err["loc"][1]: get_custom_error_message(err) for err in exc.errors()
            }
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal Server Error", status_code=500)
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(e)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.SERVICE_NAME + settings.API_V1_STR)
