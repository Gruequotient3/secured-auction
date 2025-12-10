import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiosqlite
import json

# Internals
from common.utils import errorMessage, validate_password, validate_username
from common.encrypted import rsa_decrypt, rsa_encrypt, public_server_key, private_server_key, hash_password, check_password, create_access_token
from config.config import DB_PATH, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from services.users import Users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_endpoint(
    username: str = Form(...),
    password: str = Form(...),
    public_key_e: str = Form(...),
    public_key_n: str = Form(...),
):
    private_key = private_server_key()
    username_decrypted = rsa_decrypt(username, private_key)
    password_decrypted = rsa_decrypt(password, private_key)
    password_hash = hash_password(password_decrypted)

    validate_password(password_decrypted)
    await validate_username(username_decrypted)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO UserInfo (username, password_hash, balance, created_at, public_key_e, public_key_n) VALUES (?, ?, 0, ?, ?, ?)",
            (username_decrypted, password_hash, datetime.utcnow().timestamp(), public_key_e, public_key_n),
        )
        await conn.commit()

    return JSONResponse(
        content=jsonable_encoder(
            {
                "status": "CREAT",
                "message": "OK",
            }
        )
    )


@router.post("/login")
async def login_endpoint(
    username: str = Form(...),
    password: str = Form(...),
):
    private_key = private_server_key()
    username_decrypted = rsa_decrypt(username, private_key)
    password_decrypted = rsa_decrypt(password, private_key)

    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, password_hash FROM UserInfo WHERE username = ?",
            (username_decrypted,),
        )
        row = await cursor.fetchone()

    if row is None or not check_password(password_decrypted, row["password_hash"]):
        errorMessage(401, 20, "Authentification échouée")

    user_id = row["id"]

    access_token = create_access_token({"sub": str(user_id)})

    return JSONResponse(
        content=jsonable_encoder(
            {   
                "status": "AUTHN",
                "pseudo": username_decrypted,
                "message": "OK",
                "access_token": access_token,
                "token_type": "bearer",
            }
        )
    )

@router.get("/public-key")
async def publickey_endpoint():
    public_key = public_server_key()
    return JSONResponse(
        content=jsonable_encoder(
            public_key
        )
    )