# FastAPI
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import (
    File,
    Form, 
    Depends, 
    FastAPI, 
    UploadFile, 
    HTTPException, 
)

# Builtins
import os
import re
import time

# Internals
from services.users import Users

# Externals
import aiosqlite


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


def check_price(price: float) -> bool:
    return (price >= 5.0)


def check_balance(amount):
    if(amount < 0.0):
        return False
    return True


def check_timestamp(timestamp: int) -> bool:
    now = int(time.time())
    duration = timestamp - now
    return (duration >= 120 and duration <= 60*60*24 and timestamp >= now)


def validate_password(password):
    if len(password) < 6:
        return errorMessage(400, 24, "Le mot de passe doit faire au moins six caractères")
    elif len(password) > 32:
        return errorMessage(400, 24, "Le mot de passe doit faire moins de trente deux caractères")
    else:
        return True


async def validate_username(User):
    if len(User) < 3:
        return errorMessage(400, 11, "Le pseudo doit faire au moins trois caractères")
    elif len(User) > 25:
        return errorMessage(400, 11, "Le pseudo doit faire moins de vingt cinq caractères")
    if await Users.user_exists(User):
        return errorMessage(400, 23, "Ce pseudo est déjà utilisé")
    return True