from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


PublicAccountType = Literal["user", "employer"]
AccountType = Literal["user", "employer", "admin"]


class CreateAccountRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    account_type: PublicAccountType = "user"


class CreateAccountResponse(BaseModel):
    status: Literal["ok"]
    user_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    status: Literal["ok"]
    token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    account_type: AccountType
    created_at: datetime
    updated_at: datetime
