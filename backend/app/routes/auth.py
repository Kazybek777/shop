from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import RegisterRequest, LoginRequest, GoogleLoginRequest, AuthResponse, UserResponse
from ..security import decode_access_token
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload is invalid")

    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload is invalid") from exc

    service = AuthService(db)
    return service.get_user_by_id(parsed_user_id)


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(payload)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.google_login(payload.id_token)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(user=Depends(get_current_user)):
    return UserResponse.model_validate(user)
