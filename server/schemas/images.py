from pydantic import BaseModel


class ImagesSchema(BaseModel):
    id: int
    auction_id: int
    is_cover: bool


class AddImageSchema(BaseModel):
    auction_id: int
    is_cover: bool


class RemoveImageSchema(BaseModel):
    id: int

