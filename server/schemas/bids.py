from pydantic import BaseModel


class BidSchema(BaseModel):
    id: int
    auction_id: int
    user_id: int
    created_at: int
    price: float


class CreateBidSchema(BaseModel):
    auction_id: int
    price: float


class EditBidSchema(BaseModel):
    id: int
    price: float


class GetDeleteBidSchema(BaseModel):
    id: int


class PublicBidSchema(BaseModel):
    price: float
    created_at: int
    user_id: str
