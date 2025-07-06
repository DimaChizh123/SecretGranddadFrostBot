import random

from app.db.core import connect_db

async def add_room(code: int, name: str, admin: int, username: str) -> None:
    async with connect_db() as db:
        await db.execute("INSERT INTO rooms (code, name, admin) VALUES (?, ?, ?)", (code, name, admin))
        cursor = await db.execute("SELECT id FROM rooms WHERE code = ?", (code,))
        row = await cursor.fetchone()
        if not row:
            raise ValueError("Комната не найдена")
        await db.execute("INSERT INTO users (room_id, user, username) VALUES (?, ?, ?) ON CONFLICT (room_id, user) DO UPDATE SET username = excluded.username", (row[0], admin, username))
        await db.commit()

async def check_room(code: int) -> bool:
    async with connect_db() as db:
        cursor = await db.execute("SELECT * FROM rooms WHERE code = ?", (code,))
        return await cursor.fetchone() is not None

async def generate_code() -> int:
    while True:
        code = random.randint(100000, 999999)
        async with connect_db() as db:
            cursor = await db.execute("SELECT code FROM rooms WHERE code = ?", (code,))
            row = await cursor.fetchone()
            if not row:
                return code

async def get_room_name_id(room_id: int) -> tuple[str, int] | None:
    async with connect_db() as db:
        name_cursor = await db.execute("SELECT name, code FROM rooms WHERE id = ?", (room_id,))
        row = await name_cursor.fetchone()
        if not row:
            return None
        return row

async def get_room_name_code(code: int) -> str:
    async with connect_db() as db:
        name_cursor = await db.execute("SELECT name FROM rooms WHERE code = ?", (code,))
        row = await name_cursor.fetchone()
        return row[0] if row else "Комната не найдена!"

async def delete_room_from_db(room_id: int) -> None:
    async with connect_db() as db:
        await db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        await db.execute("DELETE FROM users WHERE room_id = ?", (room_id,))
        await db.commit()