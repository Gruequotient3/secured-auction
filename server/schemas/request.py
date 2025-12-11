from typing import Optional
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    password: str
    public_key_e: str
    public_key_n: str

class LoginRequest(BaseModel):
    username: str
    password: str
    public_key_e: str
    public_key_n: str

class OtherRequests(BaseModel):
    message: str
    signature: str

class CreateAuctionRequest(BaseModel):
    title: str
    description: str
    price: float
    timestamp: int

class GetAuctionRequest(BaseModel):
    auction_id: int

class EditAuctionRequest(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    base_price: Optional[float]
    end_at: Optional[int]

    status: Optional[str]

class DeleteAuctionRequest(BaseModel):
    auction_id: int

class CreateBidRequest(BaseModel):
    auction_id: int
    price: float

class UpdatePriceRequest(BaseModel):
    auction_id: int