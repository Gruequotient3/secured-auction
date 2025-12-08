import aiosqlite
import bcrypt
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from global_functions import *

app = FastAPI()

db_path = 'database/database1.db'

async def register(User, Password):
    nid = await gen_user_id()
    validate_password(Password)
    await validate_username(User)
    hashed_password = hash_password(Password)
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("INSERT INTO userinfo (pseudo,password,balance,id) VALUES (?,?,?,?)", (User, hashed_password, 0, nid))
        await conn.commit()
    
async def gen_user_id():
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("SELECT MAX(id) FROM userinfo") as cursor:
            result = await cursor.fetchone()
            if result[0] is None:
                nid = 1
            else:
                nid = result[0] + 1
            return nid

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
    if await user_exists(User):
        return errorMessage(400, 23, "Ce pseudo est déjà utilisé")
    return True

async def user_exists(User):
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("SELECT * FROM userinfo WHERE pseudo = ?", (User,)) as cursor:
            result = await cursor.fetchone()
            if result is None:
                return False
            else:
                return True

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

async def login(User, Password):
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("SELECT password FROM userinfo WHERE pseudo = ?", (User,)) as cursor:
            result = await cursor.fetchone()
            if result is None:
                return False
            stored_password = result[0]
            return check_password(Password, stored_password)

async def add_balance(User, Amount):
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("UPDATE userinfo SET balance = balance + ? WHERE pseudo = ?", (Amount, User))
        await conn.commit()

@app.post("/register")
async def register_endpoint(
    pseudo: str = Form(...),
    password: str = Form(...)
):
    await register(pseudo, password)
    return JSONResponse(content={"message": "User registered successfully"})

@app.post("/login")
async def login_endpoint(
    pseudo: str = Form(...),
    password: str = Form(...)
):
    success = await login(pseudo, password)
    if success:
        return JSONResponse(content={"message": "Login successful"})
    else:
        errorMessage(401, 20, "Authentification échouée")

@app.post("/balance")
async def balance_endpoint(
    pseudo: str = Form(...),
    amount: float = Form(...)
):
    await add_balance(pseudo, amount)
    return JSONResponse(content={"message": "Balance updated successfully"})