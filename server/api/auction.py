# Builtins
import jwt
from datetime import datetime
from typing import List, Optional

# FASTAPI
from fastapi import (
    File,
    Form,
    Depends,
    APIRouter,
    UploadFile,
)
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials

# Database
import aiosqlite

# Internal CONFIG
from config.config import DB_PATH, SECRET_KEY, ALGORITHM
from config.loader import security
from common.utils import (
    check_title,
    check_price,
    errorMessage,
    check_description,
    check_timestamp,
)

# Schemas
from schemas.auction import (
    AuctionSchema,
    EditAuctionSchema,
    CreateAuctionSchema,
    CreateAuctionSchema,
)
from schemas.bids import (
    BidSchema,
    CreateBidSchema,
    GetDeleteBidSchema,
)
from schemas.images import (
    ImagesSchema,
    AddImageSchema,
)

# Models
from services.bids import Bid
from services.auction import Auction
from services.images import Image

# Common
from common.utils import (
    check_price, 
    check_title, 
    errorMessage, 
    check_timestamp,
    check_description, 
)

auction_router = APIRouter()



async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    if credentials is None:
        errorMessage(401, 13, "User not identified")

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        errorMessage(401, 14, "Token expired")
    except jwt.InvalidTokenError:
        errorMessage(401, 15, "Invalid token")

    raw_user_id = payload.get("sub") or payload.get("user_id")
    if raw_user_id is None:
        errorMessage(401, 16, "User id not found in token")

    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        errorMessage(401, 17, "Invalid user id in token")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM UserInfo WHERE id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()

    if row is None:
        errorMessage(401, 13, "User not identified")

    return user_id


# ---------- AUCTIONS ----------
@auction_router.post(
    "/create-auction",
    response_model=AuctionSchema,
    summary="Create a new auction with pictures",
)
async def create_auction(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    timestamp: int = Form(...),
    image: UploadFile = File(...),
    current_user_id = Depends(get_current_user),
):
    if not check_title(title):
        errorMessage(400, 32, "Title is not ok")

    if not check_description(description):
        errorMessage(400, 38, "Description is not ok")

    if not check_price(price):
        errorMessage(400, 31, "Price is not ok")

    if not check_timestamp(timestamp):
        errorMessage(400, 30, "Time is not ok")

    auction_data = CreateAuctionSchema(
        seller_id=current_user_id,
        title=title,
        description=description,
        base_price=price,
        end_at=timestamp,
    )

    auction = await Auction.create(auction_data)

    img_record = await Image.add(
        AddImageSchema(
            auction_id=auction.id,
            is_cover=True,
        )
    )

    file_path = Image.get_file_path(img_record.id)
    contents = await image.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return auction


@auction_router.post(
    "/list-auctions",
    response_model=List[AuctionSchema],
)
async def list_auctions():
    return await Auction.get_all()


@auction_router.post(
    "/get-auction",
    response_model=Optional[AuctionSchema],
    summary="Get auction by ID",
)
async def get_auction(auction_id: int = Form(...)) -> Optional[AuctionSchema]:
    auction = await Auction.get(auction_id)
    if auction is None:
        errorMessage(404, 40, "Auction not found")
    return auction


@auction_router.post(
    "/edit-auction",
    response_model=AuctionSchema,
    summary="Edit an auction",
)
async def edit_auction(
    data: EditAuctionSchema,
    current_user_id = Depends(get_current_user),
):
    existing = await Auction.get(data.id)
    if existing is None:
        errorMessage(404, 40, "Auction not found")

    if existing.seller_id != current_user_id:
        errorMessage(403, 41, "You are not the seller of this auction")

    updated = await Auction.edit(data)
    if updated is None:
        errorMessage(404, 40, "Auction not found after update")

    return updated


@auction_router.post(
    "/delete-auction",
    summary="Delete an auction",
)
async def delete_auction(
    auction_id: int = Form(...),
    current_user_id = Depends(get_current_user),
):
    existing = await Auction.get(auction_id)
    if existing is None:
        errorMessage(404, 40, "Auction not found")

    if existing.seller_id != current_user_id:
        errorMessage(403, 41, "You are not the seller of this auction")

    deleted = await Auction.delete(auction_id)
    if not deleted:
        errorMessage(404, 40, "Auction not found")

    return {"status": "OK", "deleted": True, "auction_id": auction_id}


# ---------- BIDS ----------

@auction_router.post(
    "/bid",
    response_model=BidSchema,
    summary="Create a bid",
)
async def create_bid(
    data: CreateBidSchema,
    current_user_id = Depends(get_current_user),
):
    auction = await Auction.get(data.auction_id)
    if auction is None:
        errorMessage(404, 40, "Auction not found")
    now_ts = int(datetime.utcnow().timestamp())
    if auction.end_at <= now_ts:
        errorMessage(400, 42, "Auction already finished")

    bid = await Bid.create(current_user_id, data)
    return bid


@auction_router.post(
    "/cancel-bid",
    summary="Cancel a bid",
)
async def cancel_bid(
    data: GetDeleteBidSchema,
    current_user_id = Depends(get_current_user),
):
    existing = await Bid.get(data.id)
    if existing is None:
        errorMessage(404, 43, "Bid not found")

    if existing.user_id != current_user_id:
        errorMessage(403, 44, "You are not the owner of this bid")

    deleted = await Bid.delete(data)
    if not deleted:
        errorMessage(404, 43, "Bid not found")

    return {"status": "OK", "deleted": True, "bid_id": data.id}
