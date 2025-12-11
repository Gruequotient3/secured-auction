import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiosqlite
import json

# Internals
from common.utils import errorMessage, validate_password, validate_username
from common.encrypted import rsa_decrypt, rsa_encrypt, rsa_sign, rsa_verify, public_server_key, private_server_key, hash_password, check_password, create_access_token
from config.config import DB_PATH, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from services.users import Users
from schemas.request import *

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_endpoint(
    # username: str = Form(...),
    # password: str = Form(...),
    # public_key_e: str = Form(...),
    # public_key_n: str = Form(...),
    data: RegisterRequest
):
    username = data.username
    password = data.password
    public_key_e = data.public_key_e
    public_key_n = data.public_key_n

    public_key = {
        "e": int(public_key_e),
        "n": int(public_key_n),
    }
    # if not rsa_verify(message, int(signature), public_key):
    #     errorMessage(401, 10, "Signature failed")
    # message_json = json.loads(message)
    # format_Username = int(message_json["username"])
    # format_Password = int(message_json["password"])
    format_Username = int(username)
    format_Password = int(password)
    private_key = private_server_key()
    username_decrypted = rsa_decrypt(format_Username, private_key)
    if username_decrypted == None:
        return errorMessage(400, 11, "Argument invalide")
    password_decrypted = rsa_decrypt(format_Password, private_key)
    password_hash = hash_password(password_decrypted)

    validate_password(password_decrypted)
    await validate_username(username_decrypted)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO UserInfo (username, password_hash, balance, created_at, public_key_e, public_key_n) VALUES (?, ?, 0, ?, ?, ?)",
            (username_decrypted, password_hash, datetime.utcnow().timestamp(), str(public_key_e), str(public_key_n)),
        )
        await conn.commit()

    json_Response = {
        "status": "CREAT",
        "message": "OK",
    }

    message = json.dumps(json_Response, separators=(",", ":"), sort_keys=True)

    signature = rsa_sign(message, private_key)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )


@router.post("/login")
async def login_endpoint(
    # username: str = Form(...),
    # password: str = Form(...),
    # public_key_e: str = Form(...),
    # public_key_n: str = Form(...),
    data: RegisterRequest
):
    
    username = data.username
    password = data.password
    public_key_e = data.public_key_e
    public_key_n = data.public_key_n

    format_Username = int(username)
    format_Password = int(password)
    private_key = private_server_key()
    username_decrypted = rsa_decrypt(format_Username, private_key)
    password_decrypted = rsa_decrypt(format_Password, private_key)

    async with aiosqlite.connect(DB_PATH) as conn:
        sql = "UPDATE UserInfo SET public_key_e = ?, public_key_n = ? WHERE username = ?"
        await conn.execute(sql, (public_key_e, public_key_n))
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

    username_encrypted = rsa_encrypt(username_decrypted, {"e": int(public_key_e), "n": int(public_key_n)})

    json_Response = {   
        "status": "AUTHN",
        "pseudo": username_encrypted,
        "message": "OK",
        "access_token": access_token,
        "token_type": "bearer",
    }

    message = json.dumps(json_Response, separators=(",", ":"), sort_keys=True)

    signature = rsa_sign(message, private_key)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature,
            }
        )
    )


@router.get("/public-key")
async def publickey_endpoint():
    json_Response = public_server_key()
    private_key = private_server_key()

    message = json.dumps(json_Response, separators=(",", ":"), sort_keys=True)

    signature = rsa_sign(message, private_key)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": message,
                "signature": signature
            }
        )
    )