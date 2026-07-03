from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/logout", status_code=204)
def logout(user: User = Depends(get_current_user)):
    # Stateless JWT: logout is enforced client-side by discarding the
    # tokens. For server-side revocation, swap in a refresh-token
    # denylist (e.g. Redis) keyed by token jti — noted as a future
    # enhancement in the design decisions doc.
    return None


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
