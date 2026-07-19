from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole = UserRole.viewer


class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
