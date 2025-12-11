from typing import Optional
from pydantic import BaseModel


class AuctionSchema(BaseModel):
    id: int
    seller_id: Optional[int] = None
    title: str
    description: str
    base_price: float
    created_at: int
    end_at: int

    status: str


class CreateAuctionSchema(BaseModel):
    title: str
    seller_id: int
    description: str
    base_price: float
    end_at: int


class GetDeleteAuctionSchema(BaseModel):
    id: int 


class EditAuctionSchema(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    base_price: Optional[float]
    end_at: Optional[int]

    status: Optional[str]
