from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    CONDUCTOR = "CONDUCTOR"
    PASAJERO = "PASAJERO"

class UserCreate(BaseModel):
    email: EmailStr
    plain_password: str
    name: str
    role: RoleEnum

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
