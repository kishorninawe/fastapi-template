import datetime
from collections.abc import Generator
from urllib.parse import urljoin

import pytest
from _pytest.main import Session as PytestSession
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.db import get_db, init_db
from app.core.security import create_access_token
from app.main import app
from app.models import Base

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_sessionstart(session: PytestSession) -> None:
    # Run the check before tests start
    if settings.ENVIRONMENT != "local":
        raise pytest.exit(f"Tests cannot be run in {settings.ENVIRONMENT} environment")


@pytest.fixture(scope="session", autouse=True)
def db_session() -> Generator[Session, None, None]:
    # Setup: create tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    init_db(session)
    yield session
    session.close()

    # Teardown: drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    _client = TestClient(app)
    _client.base_url = urljoin(str(_client.base_url), settings.SERVICE_NAME)
    yield _client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def user_token_headers() -> dict[str, str]:
    access_token = create_access_token(
        "dd370c1f-3e09-4bb3-b569-d7ea9cb69a35",
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "Authorization": f"Bearer {access_token}"
    }
