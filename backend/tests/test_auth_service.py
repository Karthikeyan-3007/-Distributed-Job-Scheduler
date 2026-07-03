import pytest
from fastapi import HTTPException

from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


def test_register_creates_user_with_hashed_password(db_session):
    svc = AuthService(db_session)
    user = svc.register(RegisterRequest(email="new@test.com", password="supersecret1", full_name="New User"))
    assert user.email == "new@test.com"
    assert user.hashed_password != "supersecret1"


def test_register_rejects_duplicate_email(db_session):
    svc = AuthService(db_session)
    svc.register(RegisterRequest(email="dup@test.com", password="supersecret1", full_name="A"))
    with pytest.raises(HTTPException) as exc_info:
        svc.register(RegisterRequest(email="dup@test.com", password="anotherpass1", full_name="B"))
    assert exc_info.value.status_code == 409


def test_login_succeeds_with_correct_credentials(db_session):
    svc = AuthService(db_session)
    svc.register(RegisterRequest(email="login@test.com", password="correctpass1", full_name="A"))
    tokens = svc.login(LoginRequest(email="login@test.com", password="correctpass1"))
    assert tokens.access_token
    assert tokens.refresh_token


def test_login_rejects_wrong_password(db_session):
    svc = AuthService(db_session)
    svc.register(RegisterRequest(email="wrong@test.com", password="correctpass1", full_name="A"))
    with pytest.raises(HTTPException) as exc_info:
        svc.login(LoginRequest(email="wrong@test.com", password="incorrectpass"))
    assert exc_info.value.status_code == 401


def test_refresh_issues_new_token_pair(db_session):
    svc = AuthService(db_session)
    svc.register(RegisterRequest(email="refresh@test.com", password="correctpass1", full_name="A"))
    tokens = svc.login(LoginRequest(email="refresh@test.com", password="correctpass1"))
    new_tokens = svc.refresh(tokens.refresh_token)
    assert new_tokens.access_token
    assert new_tokens.refresh_token
