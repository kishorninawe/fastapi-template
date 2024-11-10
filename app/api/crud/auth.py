import datetime

from sqlalchemy import func

from app.api.deps import SessionDep
from app.api.schemas.auth import UserRegisterSchema
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.sqltypes import decrypt


def get_user_by_email(session: SessionDep, *, email: str) -> User | None:
    # Convert the provided email to lowercase for case-insensitive comparison
    return (
        session.query(User)
        .filter(func.lower(decrypt(User.email)) == func.lower(email))
        .first()
    )


def authenticate(session: SessionDep, *, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_user(session: SessionDep, *, user_info: UserRegisterSchema) -> None:
    _now = datetime.datetime.now(datetime.UTC)
    user = User(
        email=user_info.email,
        password=get_password_hash(user_info.password),
        gender=user_info.gender,
        date_joined=_now,
        last_login=_now,
        last_active=_now,
        key_version=settings.POSTGRES_ENCRYPTION_KEY_VERSION
    )
    session.add(user)
    session.commit()
