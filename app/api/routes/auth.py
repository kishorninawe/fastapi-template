import datetime
import traceback

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response

from app.api.crud import auth
from app.api.deps import CurrentUser, SessionDep
from app.api.schemas.auth import UserRegisterSchema, UserSchema
from app.core.config import settings
from app.core.security import create_access_token
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", summary="User Registration")
async def register_user(request: Request, session: SessionDep, body: UserRegisterSchema) -> Response:
    """
    Register a new user by providing an email, password, and gender.
    """
    try:
        user = auth.get_user_by_email(session, email=body.email)
        if user:
            return JSONResponse({"detail": "The user with this email already exists"}, status_code=400)

        auth.create_user(session, user_info=body)
        return JSONResponse({"detail": "User registered successfully"}, status_code=201)
    except Exception as e:
        logger.error(f"Unexpected error while user registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/login", summary="User Login")
async def login(request: Request, session: SessionDep, body: UserSchema) -> Response:
    """
    Authenticate a user and obtain an access token by providing an email and password.
    """
    try:
        user = auth.authenticate(session, email=body.email, password=body.password)
        if not user:
            return JSONResponse({"detail": "Incorrect email or password"}, status_code=400)
        elif not user.is_active:
            return JSONResponse({"detail": "Inactive user"}, status_code=400)

        access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(str(user.id), expires_delta=access_token_expires)

        _now = datetime.datetime.now(datetime.UTC)
        user.last_login = _now
        session.commit()
        return JSONResponse(
            jsonable_encoder(
                {
                    "data": {
                        "email": user.email,
                        "access_token": access_token,
                    },
                    "detail": "Login successfully"
                }
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Unexpected error while user login: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/me", summary="Retrieve User Information")
async def user_me(request: Request, session: SessionDep, current_user: CurrentUser) -> Response:
    """
    Retrieve the authenticated user's details.
    """
    return JSONResponse(
        jsonable_encoder(
            {
                "data": {
                    "user_id": current_user.id,
                    "email": current_user.email,
                    "date_joined": current_user.date_joined,
                    "last_login": current_user.last_login,
                    "last_active": current_user.last_active,
                },
            }
        ),
        status_code=200
    )
