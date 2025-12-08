import aiosqlite
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from server.global_functions import *


router = APIRouter(prefix="/balance", tags=["balance"])

db_path = 'database/database1.db'

def check_balance(amount):
    if(amount < 0.0):
        return False
    return True

async def add_balance(User, Amount):
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("UPDATE userinfo SET balance = balance + ? WHERE pseudo = ?", (Amount, User))
        await conn.commit()

@router.post("/balance")
async def balance_endpoint(
    pseudo: str = Form(...),
    amount: float = Form(...)
):
    if not check_balance(amount):
        return errorMessage(400, 25, "Le montant n'est pas correcte")
    await add_balance(pseudo, amount)
    return JSONResponse(content={"message": "Le montant a bien été crédité"})