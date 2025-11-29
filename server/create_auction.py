from fastapi import FastAPI, HTTPException, Form, UploadFile, Depends, File
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import re
import time
import aiosqlite


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