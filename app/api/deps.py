import datetime
import json
from typing import Annotated, Any

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm.session import Session

from app.core import security
from app.core.config import settings
from app.core.db import get_db
from app.models import User

reusable_http = HTTPBearer()

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(reusable_http)]


def get_current_user(session: SessionDep, token: TokenDep) -> Any:
    # From same service
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = session.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user.last_active = datetime.datetime.now(datetime.UTC)
    session.commit()
    return user

    # From another service
    # response = requests.get(
    #     settings.AUTH_URL,
    #     headers={"Authorization": f"Bearer {token.credentials}"}
    # )
    # if response.status_code == 200:
    #     return response.json()
    #
    # try:
    #     response_json = response.json()
    # except json.JSONDecodeError:
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
    #
    # if response_json.get("detail"):
    #     raise HTTPException(status_code=response.status_code, detail=response_json.get("detail"))
    # else:
    #     raise HTTPException(status_code=403, detail="Invalid credentials")


CurrentUser = Annotated[Any, Depends(get_current_user)]
