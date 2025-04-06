from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime



class UserCreate(BaseModel):
    profilepic: Optional[str]
    name: str
    cellnumber: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    email: EmailStr
    roleId: int


class UserView(BaseModel):
    id: int
    name: str
    cellnumber: str
    email: str
    profilepic: str
    roleId: int
    created: datetime
    modified: datetime

class SuccessUserResponse(BaseModel):
    success: bool
    message: str
    data: UserView

class UserUpdate(BaseModel):
    profilepic: Optional[str] = None
    name: Optional[str] = None
    cellnumber: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    roleId: Optional[int] = None
    
class UserResponse(BaseModel):
    success: bool
    message: str
    data: UserView

class LoginRequest(BaseModel):
    cellnumber: str
    password: str


class Token(BaseModel):
    token: str
    ttl: int
    userId: int
    created: datetime
