import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiosqlite
import json

# Internals
from common.utils import errorMessage
from common.encrypted import hash_password, check_password, create_access_token
from config.config import DB_PATH, RSA_KEYS_PATH, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_endpoint(
    username: str = Form(...),
    password: str = Form(...),
):
    password_hash = hash_password(password)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO UserInfo (username, password_hash, balance, created_at) VALUES (?, ?, 0, ?)",
            (username, password_hash, datetime.utcnow().timestamp()),
        )
        await conn.commit()

    return JSONResponse(content=jsonable_encoder({"status": "CREAT", "message": "OK"}))


@router.post("/login")
async def login_endpoint(
    username: str = Form(...),
    password: str = Form(...),
):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, password_hash FROM UserInfo WHERE username = ?",
            (username,),
        )
        row = await cursor.fetchone()

    if row is None or not check_password(password, row["password_hash"]):
        errorMessage(401, 20, "Authentification échouée")

    user_id = row["id"]

    access_token = create_access_token({"sub": str(user_id)})

    return JSONResponse(
        content=jsonable_encoder(
            {
                "access_token": access_token,
                "token_type": "bearer",
            }
        )
    )

@router.get("/public-key")
async def publickey_endpoint():
    json_data = open(RSA_KEYS_PATH)
    keys = json.load(json_data)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "e": int(keys["e"]),
                "n": int(keys["n"])
            }
        )
    )