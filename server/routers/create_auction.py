from fastapi import APIRouter, Form, UploadFile, Depends, File
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import time
import aiosqlite
import os

from global_functions import *


router = APIRouter(prefix="/create-auction", tags=["create-auction"])

dbPath = "database/database1.db"

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials = Depends(security)):
    if credentials is None:
        errorMessage(401, 13, "L'utilisateur n'est pas authentifié")
    token = credentials.credentials
    async with aiosqlite.connect(dbPath) as db: 
        user = await get_user_by_token(token, db)
        if not user:
            errorMessage(401, 13, "L'utilisateur n'est pas authentifié")
        return user[3]

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


@router.post("/create-auction")
async def create_auction(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    timestamp: int = Form(...),
    image: UploadFile = File(...),
    current_user = Depends(get_current_user)
) :
    titleResult = check_title(title)
    if(titleResult != 0):
        if(titleResult == 1):
            return errorMessage(400, 32, "Le titre est trop court")
        if(titleResult == 2):
            return errorMessage(400, 32, "Le titre est trop long")
        if(titleResult == 3):
            return errorMessage(400, 32, "Le titre contient des caractères non acceptés")
        
    descriptionResult = check_description(description)
    if(descriptionResult != 0):
        if(descriptionResult == 1):
            return errorMessage(400, 38, "La description est trop courte")
        if(descriptionResult == 2):
            return errorMessage(400, 38, "La description est trop longue")
        if(descriptionResult == 3):
            return errorMessage(400, 38, "La description contient des caractères non acceptés")

    if not check_price(price):
        return errorMessage(400, 31, "Le prix doit être au moins 5.00 euros")

    timestampResult = check_timestamp(timestamp)
    if(timestampResult != 0):
        if(timestampResult == 1):
            return errorMessage(400, 30, "La durée doit être au moins 2 minutes")
        if(timestampResult == 2):
            return errorMessage(400, 30, "La durée doit être inférieur à 24 heures")
        if(timestampResult == 3):
            return errorMessage(400, 30, "La durée n'est pas correcte")
    
    return await addAuctionToDatabase(title, description, price, image, timestamp, current_user)