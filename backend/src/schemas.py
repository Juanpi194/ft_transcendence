from pydantic import BaseModel, EmailStr, Field
from .core import USERNAME_MIN_LEN, USERNAME_MAX_LEN, \
    PASSWORD_MIN_LEN


class UserCreate(BaseModel):
    username: str = Field(..., min_length=USERNAME_MIN_LEN,
                          max_length=USERNAME_MAX_LEN)
    email_str: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LEN)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
