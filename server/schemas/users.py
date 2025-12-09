from typing import Optional
from pydantic import BaseModel


class UserSchema(BaseModoel):
    id: str
    username: str
    balance: float
    public_key: Optional[str]
    created_at: int


class CreateUserSchema(BaseModoel):
    username: str
    password: str
    public_key: Optional[str]


class EditUserSchema(BaseModoel):
    id: str
    username: str
    public_key: Optional[str]
    balance: float


class GetDeleteUserSchema(BaseModoel):
    id: str


class PublicUserSchema(BaseModoel):
    id: str
    username: str
