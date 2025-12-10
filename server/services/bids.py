# Builtins
from typing import Optional
from datetime import datetime

# Database
import aiosqlite

# Internals
from schemas.bids import (
    BidSchema,
    CreateBidSchema,
    EditBidSchema,
    GetDeleteBidSchema,
)
from config.config import DB_PATH


class Bid:
    @staticmethod
    async def _row_to_schema(row: aiosqlite.Row) -> BidSchema:
        return BidSchema(
            id=row["id"],
            auction_id=row["auction_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            price=row["price"],
        )

    @staticmethod
    async def create(user_id: int, data: CreateBidSchema) -> BidSchema:
        created_at = int(datetime.utcnow().timestamp())

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = """
                INSERT INTO Bids (auction_id, user_id, created_at, price)
                VALUES (?, ?, ?, ?)
            """
            cursor = await db.execute(
                sql,
                (
                    data.auction_id,
                    user_id,
                    created_at,
                    data.price,
                ),
            )
            await db.commit()

            bid_id = cursor.lastrowid

            return BidSchema(
                id=bid_id,
                auction_id=data.auction_id,
                user_id=user_id,
                created_at=created_at,
                price=data.price,
            )

    @staticmethod
    async def get(bid_id: int) -> Optional[BidSchema]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Bids WHERE id = ?"
            cursor = await db.execute(sql, (bid_id,))
            row = await cursor.fetchone()

        if row is None:
            return None

        return await Bid._row_to_schema(row)

    @staticmethod
    async def get_last_bid(auction_id: int) -> Optional[BidSchema]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Bids WHERE auction_id = ? ORDER BY created_at DESC LIMIT 1"
            cursor = await db.execute(sql, (auction_id,))
            row = await cursor.fetchone()

        if row is None:
            return None

        return await Bid._row_to_schema(row)

    @staticmethod
    async def edit(data: EditBidSchema) -> Optional[BidSchema]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = """
                UPDATE Bids
                SET price = ?
                WHERE id = ?
            """
            cursor = await db.execute(
                sql,
                (
                    data.price,
                    data.id,
                ),
            )
            await db.commit()

            if cursor.rowcount == 0:
                return None

        return await Bid.get(data.id)

    @staticmethod
    async def delete(bid: GetDeleteBidSchema) -> bool:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = "DELETE FROM Bids WHERE id = ?"
            cursor = await db.execute(sql, (bid.id,))
            await db.commit()

            return cursor.rowcount > 0
