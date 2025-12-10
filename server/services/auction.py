# Builtins
from datetime import datetime
from typing import Optional, List
from threading import Thread
import asyncio

# Database
import aiosqlite

# Internals
from config.config import DB_PATH
from schemas.auction import (
    AuctionSchema,
    EditAuctionSchema,
    CreateAuctionSchema,
    GetDeleteAuctionSchema,
)


class Auction:
    @staticmethod
    async def _row_to_schema(row: aiosqlite.Row) -> AuctionSchema:
        return AuctionSchema(
            id=row["id"],
            seller_id=row["seller_id"],
            title=row["title"],
            description=row["description"],
            base_price=row["base_price"],
            created_at=row["created_at"],
            end_at=row["end_at"],
            status=row["status"],
        )

    @staticmethod
    async def create(data: CreateAuctionSchema) -> AuctionSchema:
        """
        Creates a new auction in the database.
        Returns the created AuctionSchema.
        """
        # Попробуем достать seller_id из data
        seller_id = data.seller_id
        if seller_id is None:
            raise ValueError("CreateAuctionSchema must contain seller_id for create_auction")

        created_at = int(datetime.utcnow().timestamp())

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = """
                INSERT INTO Auctions (seller_id, title, description, base_price, created_at, end_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor = await db.execute(
                sql,
                (
                    seller_id,
                    data.title,
                    data.description,
                    data.base_price,
                    created_at,
                    data.end_at,
                    "ACTIVE",
                ),
            )
            await db.commit()

            auction_id = cursor.lastrowid

            return AuctionSchema(
                id=auction_id,
                seller_id=seller_id,
                title=data.title,
                description=data.description,
                base_price=data.base_price,
                created_at=created_at,
                end_at=data.end_at,
                status="ACTIVE",
            )

    @staticmethod
    async def get(auction_id: int) -> Optional[AuctionSchema]:
        """
        Returns AuctionShema by auction_id or None if not found.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Auctions WHERE id = ?"
            cursor = await db.execute(sql, (auction_id,))
            row = await cursor.fetchone()

        if row is None:
            return None

        return await Auction._row_to_schema(row)

    @staticmethod
    async def edit(data: EditAuctionSchema) -> Optional[AuctionSchema]:
        """
        Updates auction details in the database.
        Returns updated AuctionSchema or None if auction not found.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = """
                UPDATE Auctions
                SET title = ?,
                    description = ?,
                    base_price = ?,
                    end_at = ?,
                    status = ?
                WHERE id = ?
            """
            cursor = await db.execute(
                sql,
                (
                    data.title,
                    data.description,
                    data.base_price,
                    data.end_at,
                    data.status,
                    data.id,
                ),
            )
            await db.commit()

            if cursor.rowcount == 0:
                return None

        return await Auction.get_auction(data.id)

    @staticmethod
    async def delete(auction_id: int) -> bool:
        """
        Removes auction from the database.
        Returns True if auction was deleted, False if not found.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = "DELETE FROM Auctions WHERE id = ?"
            cursor = await db.execute(sql, (auction_id,))
            await db.commit()

            return cursor.rowcount > 0

    @staticmethod
    async def get_all() -> List[AuctionSchema]:
        """
        Returns a list of all auctions.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Auctions"
            cursor = await db.execute(sql)
            rows = await cursor.fetchall()

        return [await Auction._row_to_schema(row) for row in rows]
    
    @staticmethod
    async def get_auctions_user_is_in(user_id):
        """
        Returns a list of all the auctions the user is in.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Auction_Participants WHERE user_id = ?"
            cursor = await db.execute(sql, (user_id, ))
            rows = await cursor.fetchall()

            return [await Auction._row_to_schema(row) for row in rows]

    @staticmethod
    async def auctions_status():
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Auction WHERE status = ?"
            cursor = await db.execute(sql, ("ACTIVE", ))
            rows = await cursor.fetchall()

            for row in rows:
                if row["end_at"] >= int(datetime.utcnow().timestamp()):
                    sql_update = "UPDATE Auction SET status = ? WHERE auction_id = ?"
                    await db.execute(sql_update, ("INACTIVE", row["auction_id"], ))
                    await db.commit()

                    sql_update = "SELECT * FROM Bids WHERE auction_id = ? ORDER BY price DESC LIMIT 1"
                    cursor_update = await db.execute(sql_update, (row["auction_id"], ))
                    row_winner_bid = await cursor_update.fetchone()

                    if row_winner_bid == None:
                        continue

                    final_bid = float(row_winner_bid["price"])

                    sql_update = "SELECT * FROM UserInfo WHERE id = ?"
                    cursor_update = await db.execute(sql_update, (row_winner_bid["user_id"], ))
                    row_winner = await cursor_update.fetchone()

                    winner_new_balance = float(row_winner["balance"]) - final_bid

                    sql_update = "SELECT * FROM UserInfo WHERE id = ?"
                    cursor_update = await db.execute(sql_update, (row["seller_id"], ))
                    row_seller = await cursor_update.fetchone()

                    seller_new_balance = float(row_seller["balance"]) + final_bid

                    sql_update = "UPDATE UserInfo SET balance = ? WHERE id = ?"
                    await db.execute(sql_update, (winner_new_balance, row_winner["id"], ))
                    await db.commit()

                    sql_update = "UPDATE UserInfo SET balance = ? WHERE id = ?"
                    await db.execute(sql_update, (seller_new_balance, row_seller["id"], ))
                    await db.commit()

            # if active and time over -> inactive then credit seller account and debit bidder
    
    @staticmethod
    async def check_auctions_status():
        while True:
            await Auction.auctions_status()
            await asyncio.sleep(5)



