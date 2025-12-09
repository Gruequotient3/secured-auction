# Builtins
from datetime import datetime
from typing import Optional, List

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
