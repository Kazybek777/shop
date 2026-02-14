import json
from datetime import datetime, timezone
from urllib import parse, request, error

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import settings
from ..repositories.user_repository import UserRepository
from ..schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from ..security import hash_password, verify_password, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register(self, payload: RegisterRequest) -> AuthResponse:
        email = payload.email.strip().lower()
        if self.user_repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = self.user_repository.create(
            email=email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            provider="local",
            role=self._resolve_role_for_email(email),
        )
        return self._build_auth_response(user.id)

    def login(self, payload: LoginRequest) -> AuthResponse:
        email = payload.email.strip().lower()
        user = self.user_repository.get_by_email(email)
        if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        return self._build_auth_response(user.id)

    def google_login(self, id_token: str) -> AuthResponse:
        claims = self._verify_google_id_token(id_token)

        google_sub = claims.get("sub")
        email = (claims.get("email") or "").strip().lower()
        full_name = claims.get("name") or claims.get("given_name") or "Google User"

        if not google_sub or not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token payload is invalid")

        user = self.user_repository.get_by_google_sub(google_sub)
        if user is None:
            user = self.user_repository.get_by_email(email)

        if user is None:
            user = self.user_repository.create(
                email=email,
                full_name=full_name,
                provider="google",
                google_sub=google_sub,
                hashed_password=None,
                role=self._resolve_role_for_email(email),
            )
        else:
            update_fields = {}
            if not user.google_sub:
                update_fields["google_sub"] = google_sub
            if user.provider != "google":
                update_fields["provider"] = "google"
            desired_role = self._resolve_role_for_email(email)
            if user.role != desired_role and desired_role == "admin":
                update_fields["role"] = desired_role
            if update_fields:
                user = self.user_repository.update(user, **update_fields)

        return self._build_auth_response(user.id)

    def get_user_by_id(self, user_id: int):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    def _build_auth_response(self, user_id: int) -> AuthResponse:
        user = self.get_user_by_id(user_id)
        token = create_access_token(str(user.id))
        return AuthResponse(access_token=token, user=UserResponse.model_validate(user))

    def _verify_google_id_token(self, id_token: str) -> dict:
        if not settings.google_client_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google auth is not configured")

        query = parse.urlencode({"id_token": id_token})
        url = f"https://oauth2.googleapis.com/tokeninfo?{query}"

        try:
            with request.urlopen(url, timeout=10) as response:
                body = response.read().decode("utf-8")
                claims = json.loads(body)
        except error.HTTPError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token") from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to verify Google token") from exc

        aud = claims.get("aud")
        exp_raw = claims.get("exp")
        email_verified = claims.get("email_verified") in ("true", True)

        if aud != settings.google_client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token audience mismatch")

        try:
            exp = int(exp_raw)
        except (TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token expiration is invalid")

        if exp <= int(datetime.now(timezone.utc).timestamp()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token is expired")

        if not email_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google account email is not verified")

        return claims

    def _resolve_role_for_email(self, email: str) -> str:
        normalized_admin_emails = {admin_email.strip().lower() for admin_email in settings.admin_emails}
        if email in normalized_admin_emails:
            return "admin"
        if not normalized_admin_emails and self.user_repository.count_by_role("admin") == 0:
            return "admin"
        return "user"
