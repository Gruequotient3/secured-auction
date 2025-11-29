from fastapi import FastAPI, HTTPException, Form, UploadFile, Depends, File
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import re
import time
import aiosqlite
import os


app = FastAPI(title="Secured Auction")

dbPath = "database/database1.db"

security = HTTPBearer(auto_error=False)


async def get_user_by_token(token, db):
    sqlRequest = "select * FROM userinfo WHERE sessionId = ?"
    cursor = await db.execute(sqlRequest, (token, ))
    userInfo = await cursor.fetchone()
    return userInfo

async def get_current_user(credentials = Depends(security)):
    if credentials is None:
        errorMessage(401, 13, "User not identified")
    token = credentials.credentials
    async with aiosqlite.connect(dbPath) as db: 
        user = await get_user_by_token(token, db)
        if not user:
            errorMessage(401, 13, "User not identified")
        return user[3]

def errorMessage(status_code: int, code: int, message: str):
    raise HTTPException(
        status_code = status_code,
        detail = {
            "status": "ERROR",
            "code": code,
            "message": message
        }
    )

def check_title(title: str) -> bool:
    return (len(title) > 3 and re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ]*", title, flags=re.UNICODE) and len(title) < 15)

def check_description(description: str) -> bool:
    return (len(description) > 3 and re.fullmatch(r"[\w\s\-',.]*", description, flags=re.UNICODE) and len(description) < 80)

def check_timestamp(timestamp: int) -> bool:
    now = int(time.time())
    duration = timestamp - now
    return (duration >= 120 and duration <= 60*60*24 and timestamp >= now)

def check_price(price: float) -> bool:
    return (price >= 5.0)

async def gen_id(db) -> int:
    newId = 1
    while(True):
        sqlRequest = "select * FROM auctions WHERE id = ?"
        cursor = await db.execute(sqlRequest, (newId, ))
        id = await cursor.fetchone()
        if not id:
            return newId
        newId += 1

def saveImage(file: UploadFile, auctionId: int) -> str:
    folder = f'auctionImages/{auctionId}/'
    os.makedirs(folder, exist_ok=True)
    imagePath = os.path.join(folder, 'image.jpg')
    with open(imagePath, 'wb') as image:
        image.write(file.file.read())
    return imagePath


async def addAuctionToDatabase(title: str, description: str, price: float, image: UploadFile, timestamp: int, userId: int):    
    async with aiosqlite.connect(dbPath) as db:
        newId = await gen_id(db)
        imagePath = saveImage(image, newId)
        now = int(time.time())
        sqlRequest = "INSERT INTO auctions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor = await db.execute(sqlRequest, (title, description, imagePath, newId, price, 0.0, 0, "", userId, now, timestamp))
        await db.commit()
        jsonResponse = {
            "status": "NAUCT",
            "auctionId": newId,
            "title": title,
            "initialPrice": price,
            "endsAt": timestamp,
        }
        return JSONResponse(content=jsonable_encoder(jsonResponse))


@app.post("/create-auction")
async def create_auction(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    timestamp: int = Form(...),
    image: UploadFile = File(...),
    current_user = Depends(get_current_user)
) :
    if not check_title(title):
        return errorMessage(400, 32, "Title is not ok")

    if not check_description(description):
        return errorMessage(400, 38, "Description is not ok")

    if not check_price(price):
        return errorMessage(400, 31, "Price is not ok")

    if not check_timestamp(timestamp):
        return errorMessage(400, 30, "Time is not ok")
    
    return await addAuctionToDatabase(title, description, price, image, timestamp, current_user)