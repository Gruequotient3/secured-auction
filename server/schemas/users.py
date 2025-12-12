from typing import Optional
from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str
    username: str
    balance: float
    public_key_e: str
    public_key_n: str
    created_at: int


class CreateUserSchema(BaseModel):
    username: str
    password: str
    public_key: Optional[str]


class EditUserSchema(BaseModel):
    id: str
    username: str
    public_key: Optional[str]
    balance: float


class GetDeleteUserSchema(BaseModel):
    id: str


class PublicUserSchema(BaseModel):
    id: str
    username: str
