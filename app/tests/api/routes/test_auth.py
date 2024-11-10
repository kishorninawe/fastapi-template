from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.crud.auth import get_user_by_email
from app.core.security import verify_password


def test_register_user(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/api/v1/register",
        json={"email": "test@gmail.com", "password": "12345", "gender": "Male"}
    )

    assert response.status_code == 201
    content = response.json()
    assert content["detail"] == "User registered successfully"

    user = get_user_by_email(db_session, email="test@gmail.com")
    assert user
    assert user.email == "test@gmail.com"
    assert user.gender == "Male"
    assert verify_password("12345", user.password)


def test_register_user_email_already_exists_error(client: TestClient) -> None:
    response = client.post(
        "/api/v1/register",
        json={"email": "johndoe@gmail.com", "password": "12345", "gender": "Male"}
    )

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "The user with this email already exists"


def test_register_user_email_already_exists_error_case_insensitive(client: TestClient) -> None:
    response = client.post(
        "/api/v1/register",
        json={"email": "JohnDoe@Gmail.com", "password": "12345", "gender": "Male"}
    )

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "The user with this email already exists"


def test_login(client: TestClient) -> None:
    response = client.post(
        "/api/v1/login",
        json={"email": "johndoe@gmail.com", "password": "12345"}
    )

    assert response.status_code == 200
    content = response.json()
    assert content["detail"] == "Login successfully"
    assert "data" in content
    data = content["data"]
    assert data["email"] == "johndoe@gmail.com"
    assert "access_token" in data
    assert data["access_token"]


def test_login_case_insensitive(client: TestClient) -> None:
    response = client.post(
        "/api/v1/login",
        json={"email": "JohnDoe@Gmail.com", "password": "12345"}
    )

    assert response.status_code == 200
    content = response.json()
    assert content["detail"] == "Login successfully"
    assert "data" in content
    data = content["data"]
    assert data["email"] == "johndoe@gmail.com"
    assert "access_token" in data
    assert data["access_token"]


def test_login_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/login",
        json={"email": "invalid@gmail.com", "password": "12345"}
    )

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Incorrect email or password"


def test_login_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/login",
        json={"email": "johndoe@gmail.com", "password": "invalid"}
    )

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Incorrect email or password"


def test_login_inactive(client: TestClient, db_session: Session) -> None:
    user = get_user_by_email(db_session, email="johndoe@gmail.com")
    assert user

    user.is_active = False
    db_session.commit()

    response = client.post(
        "/api/v1/login",
        json={"email": "johndoe@gmail.com", "password": "12345"}
    )

    user.is_active = True
    db_session.commit()

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Inactive user"


def test_register_user_me(client: TestClient, user_token_headers: dict[str, str]) -> None:
    response = client.get(
        "/api/v1/me",
        headers=user_token_headers
    )

    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    data = content["data"]

    expected_data_fields = {"user_id", "email", "date_joined", "last_login", "last_active"}
    assert set(data.keys()) == expected_data_fields
    assert data["user_id"] == "dd370c1f-3e09-4bb3-b569-d7ea9cb69a35"
    assert data["email"] == "johndoe@gmail.com"
