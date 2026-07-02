from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


PublicAccountType = Literal["candidate", "employer"]
AccountType = Literal["candidate", "employer", "admin"]


class CreateAccountRequest(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(min_length=1)
    password: str = Field(min_length=8)
    account_type: PublicAccountType = "candidate"


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
    full_name: str | None = None
    email: EmailStr
    phone: str | None = None
    account_type: AccountType
    company_name: str | None = None
    company_logo_url: str | None = None
    created_at: datetime
    updated_at: datetime
