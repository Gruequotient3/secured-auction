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
from fastapi.encoders import jsonable_encoder


# Database
import aiosqlite

# Internal CONFIG
from config.config import DB_PATH, SECRET_KEY, ALGORITHM
from config.loader import security
from common.encrypted import rsa_decrypt, rsa_encrypt, rsa_sign, rsa_verify, public_server_key, private_server_key, hash_password, check_password, create_access_token
from common.utils import (
    check_title,
    check_price,
    errorMessage,
    check_description,
    check_timestamp,
)

from common.encrypted import *

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

from schemas.request import *

# Models
from services.bids import Bid
from services.auction import Auction
from services.images import Image
from services.users import Users

# Common
from common.utils import (
    check_price, 
    check_title, 
    errorMessage, 
    check_timestamp,
    check_description,
    check_balance,
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
    response_model=Optional[AuctionSchema],
    summary="Create a new auction with pictures",
)
async def create_auction(
    # title: str = Form(...),
    # description: str = Form(...),
    # price: float = Form(...),
    # timestamp: int = Form(...),
    data: OtherRequests,
    # image: UploadFile = File(...),
    current_user_id = Depends(get_current_user),
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    title = message_dict["title"]
    description = message_dict["description"]
    price = int(message_dict["price"])
    timestamp = int(message_dict["timestamp"])    

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

    # img_record = await Image.add(
    #     AddImageSchema(
    #         auction_id=auction.id,
    #         is_cover=True,
    #     )
    # )

    # file_path = Image.get_file_path(img_record.id)
    # contents = await image.read()
    # with open(file_path, "wb") as f:
    #     f.write(contents)


    private_key = private_server_key()
    auction_dict = auction.model_dump(mode='json')
    message = json.dumps(auction_dict, separators=(",", ":"), sort_keys=True)

    signature = rsa_sign(message, private_key)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )   


@auction_router.post(
    "/list-auctions",
    response_model=Optional[List[AuctionSchema]],
)
async def list_auctions():
    private_key = private_server_key()
    auctions = await Auction.get_all()
    auctions_dict = [auction.model_dump(mode="json") for auction in auctions]
    message = json.dumps(auctions_dict, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )  


@auction_router.post(
    "/get-auction",
    response_model=Optional[AuctionSchema],
    summary="Get auction by ID",
)
async def get_auction(
    # auction_id: int = Form(...)
    data: OtherRequests,
    current_user_id = Depends(get_current_user),
) -> Optional[AuctionSchema]:
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    auction_id = message_dict["auction_id"]

    private_key = private_server_key()
    auction = await Auction.get(auction_id)
    if auction is None:
        errorMessage(404, 40, "Auction not found")

    auction_dict = auction.model_dump(mode='json')
    message = json.dumps(auction_dict, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )  



@auction_router.post(
    "/delete-auction",
    summary="Delete an auction",
)
async def delete_auction(
    # auction_id: int = Form(...),
    data: OtherRequests,
    current_user_id = Depends(get_current_user),
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    auction_id = message_dict["auction_id"]    

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
    response_model=Optional[BidSchema],
    summary="Create a bid",
)
async def create_bid(
    # data: CreateBidSchema,
    data: OtherRequests,
    current_user_id = Depends(get_current_user),
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    auction_id = message_dict["auction_id"]

    auction = await Auction.get(auction_id)
    if auction is None:
        errorMessage(404, 40, "Auction not found")
    now_ts = int(datetime.utcnow().timestamp())
    if auction.end_at <= now_ts:
        errorMessage(400, 42, "Auction already finished")
        
    user = await Users.get(current_user_id)
    if user.balance < float(message_dict["price"]):
        errorMessage(400, 47, "Insufficient credit")



    bidData = CreateBidSchema(
        auction_id=auction_id,
        price=float(message_dict["price"])
    )

    bid = await Bid.create(current_user_id, bidData)
    private_key = private_server_key()
    bid_dict = bid.model_dump(mode='json')
    message = json.dumps(bid_dict, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )


@auction_router.post(
    "/update-price",
    summary="Update the price of an auction"
)
async def update_price(
    # auction_id: int = Form(...),
    data: OtherRequests,
    current_user_id = Depends(get_current_user)
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    auction_id = message_dict["auction_id"]

    auction = await Auction.get(auction_id)
    if auction is None:
        errorMessage(404, 40, "Auction not found")
    updated_price = await Bid.get_highest(auction_id)
    private_key = private_server_key()
    json_response = {
        "auction_id": auction_id,
        "updated_price": updated_price
    }
    message = json.dumps(json_response, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )


@auction_router.post(
    "/cancel-bid",
    summary="Cancel a bid",
)
async def cancel_bid(
    data: OtherRequests,
    # data: GetDeleteBidSchema,
    current_user_id = Depends(get_current_user),
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    bid_id = message_dict["bid_id"]

    existing = await Bid.get(bid_id)
    if existing is None:
        errorMessage(404, 43, "Bid not found")

    if existing.user_id != current_user_id:
        errorMessage(403, 44, "You are not the owner of this bid")


    now_ts = int(datetime.utcnow().timestamp())
    if (now_ts - existing.created_at) > 10:
        errorMessage(400, 45, "You cannot cancel a bid after 10 seconds")

    last_bid = await Bid.get_last_bid(existing.auction_id)
    if last_bid is None:
        errorMessage(404, 43, "Bid not found")

    if last_bid.id != existing.id:
        errorMessage(400, 46, "You can only cancel your bid if it is the latest one")

    deleted = await Bid.delete(bid_id)
    if not deleted:
        errorMessage(404, 43, "Bid not found")

    private_key = private_server_key()

    json_response = {
        "status": "CNBID",
        "message": "OK"
    }

    message = json.dumps(json_response, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )

@auction_router.post(
    "/balance",
    summary="Add credit to account",
)
async def balance_endpoint(
    data: OtherRequests,
    current_user_id = Depends(get_current_user)
    # amount: float = Form(...),
):
    message = data.message
    signature = data.signature

    user_public_key = await Users.get_user_public_key(current_user_id)

    if not rsa_verify(message, signature, user_public_key):
        errorMessage(401, 00, "Signature verification failed")

    try:
        message_dict = json.loads(message)
    except:
        errorMessage(400, 00, "Invalid JSON in message")

    amount = float(message_dict["amount"])

    if not check_balance(amount):
        return errorMessage(400, 25, "Le montant n'est pas correcte")
    await Users.add_balance(current_user_id, amount)
    private_key = private_server_key()
    json_response = {
        "status": "OK",
        "message": "Le montant a bien été crédité"
    }

    message = json.dumps(json_response, separators=(",", ":"), sort_keys=True)
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )


@auction_router.get(
    "/get-balance",
    summary="Get the account balance",
)
async def get_balance_endpoint(
    current_user_id = Depends(get_current_user),
):
    user_balance = await Users.get_user_balance(current_user_id)
    private_key = private_server_key()
    json_response = {
        "balance": user_balance,
    }


    message = json.dumps(json_response, separators=(",", ":"),
     sort_keys=True)
    print(message);
    signature = rsa_sign(message, private_key)
    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )