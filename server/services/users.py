# Builtins
from datetime import datetime
from typing import Optional, List

# Database
import aiosqlite

# Internals
from config.config import DB_PATH
from schemas.users import (
    UserSchema,
    CreateUserSchema,
    EditUserSchema,
    GetDeleteUserSchema,
    PublicUserSchema,
)

class Users:
    @staticmethod
    async def gen_user_id():
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute("SELECT MAX(id) FROM UserInfo") as cursor:
                result = await cursor.fetchone()
                if result[0] is None:
                    nid = 1
                else:
                    nid = result[0] + 1
                return nid
    
    @staticmethod
    async def user_exists(username: str):
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute("SELECT * FROM UserInfo WHERE username = ?", (username,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    return False
                else:
                    return True

    @staticmethod   
    async def add_balance(user_id, amount):
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute("UPDATE UserInfo SET balance = balance + ? WHERE id = ?", (amount, user_id))
            await conn.commit()