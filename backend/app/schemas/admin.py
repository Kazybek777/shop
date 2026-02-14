from pydantic import BaseModel, Field


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(user|admin)$")


class MessageResponse(BaseModel):
    message: str
