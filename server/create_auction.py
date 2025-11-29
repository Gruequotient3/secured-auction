from fastapi import FastAPI, HTTPException
import re
import time

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
