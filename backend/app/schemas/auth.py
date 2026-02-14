from pydantic import BaseModel, Field
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    provider: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    full_name: str = Field(..., min_length=2, max_length=120)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., min_length=10)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
