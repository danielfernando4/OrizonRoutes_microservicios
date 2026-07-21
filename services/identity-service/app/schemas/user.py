import re

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from enum import Enum


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>_\-]).{8,}$"
)


class RoleEnum(str, Enum):
    CONDUCTOR = "conductor"
    PASAJERO = "pasajero"


class UserCreate(BaseModel):
    email: EmailStr
    plain_password: str
    name: str
    role: RoleEnum

    @field_validator("plain_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres, "
                "una mayúscula, una minúscula, un número y un carácter especial"
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    plain_password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
