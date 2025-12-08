from fastapi import HTTPException
import time
import re

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
    if(len(title) < 3):
        return 1
    if(len(title) > 15):
        return 2
    if not (re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ]*", title, flags=re.UNICODE)):
        return 3
    return 0

def check_description(description: str) -> bool:
    if(len(description) < 3):
        return 1
    if(len(description) > 80):
        return 2
    if not (re.fullmatch(r"[\w\s\-',.]*", description, flags=re.UNICODE)):
        return 3
    return 0

def check_timestamp(timestamp: int) -> bool:
    now = int(time.time())
    duration = timestamp - now
    if(duration < 120):
        return 1
    if(duration > 60*24*24):
        return 2
    if(timestamp < now):
        return 3
    return 0

def check_price(price: float) -> bool:
    return (price >= 5.0)


async def get_user_by_token(token, db):
    sqlRequest = "select * FROM userinfo WHERE sessionId = ?"
    cursor = await db.execute(sqlRequest, (token, ))
    userInfo = await cursor.fetchone()
    return userInfo