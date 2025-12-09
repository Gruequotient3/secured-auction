import os
from typing import Optional, List

import aiosqlite

# Internals
from config.config import DB_PATH, IMAGES_DIR
from schemas.images import (
    ImagesSchema,
    AddImageSchema,
    RemoveImageSchema,
)


class Image:
    @staticmethod
    def get_file_path(image_id: int) -> str:
        """
        Get filepath by id.
        """
        os.makedirs(IMAGES_DIR, exist_ok=True)
        return os.path.join(IMAGES_DIR, f"{image_id}.json")

    @staticmethod
    async def _row_to_schema(row: aiosqlite.Row) -> ImagesSchema:
        return ImagesSchema(
            id=row["id"],
            auction_id=row["auction_id"],
            is_cover=bool(row["is_cover"]),
        )

    @staticmethod
    async def add(data: AddImageSchema) -> ImagesSchema:
        """
        Creates an Image instance in database and returns it as ImagesSchema.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = """
                INSERT INTO Images (auction_id, is_cover)
                VALUES (?, ?)
            """
            cursor = await db.execute(
                sql,
                (
                    data.auction_id,
                    data.is_cover,
                ),
            )
            await db.commit()

            image_id = cursor.lastrowid

        return ImagesSchema(
            id=image_id,
            auction_id=data.auction_id,
            is_cover=data.is_cover,
        )

    @staticmethod
    async def get(image_id: int) -> Optional[ImagesSchema]:
        """
        Get image by Id.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Images WHERE id = ?"
            cursor = await db.execute(sql, (image_id,))
            row = await cursor.fetchone()

        if row is None:
            return None

        return await Image._row_to_schema(row)

    @staticmethod
    async def get_all_by_auction(auction_id: int) -> List[ImagesSchema]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            sql = "SELECT * FROM Images WHERE auction_id = ?"
            cursor = await db.execute(sql, (auction_id,))
            rows = await cursor.fetchall()

        return [await Image._row_to_schema(row) for row in rows]

    @staticmethod
    async def remove(image_id: int, delete_file: bool = True) -> bool:
        """
        Deletes records from the Images table.
        If delete_file=True, also tries to delete the {id}.json file.
        Returns True if the record was deleted.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("PRAGMA foreign_keys = ON;")

            sql = "DELETE FROM Images WHERE id = ?"
            cursor = await db.execute(sql, (image_id,))
            await db.commit()

            deleted = cursor.rowcount > 0

        if deleted and delete_file:
            file_path = Image.get_file_path(image_id)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    # можно залогировать, но не валить весь запрос
                    pass

        return deleted
