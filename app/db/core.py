import os
from contextlib import asynccontextmanager

import aiosqlite

DB_PATH = os.getenv("DB_PATH", "secret_santa.db")

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            code INTEGER UNIQUE, 
            name TEXT, 
            admin BIGINT
        )""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
            room_id INTEGER, 
            user BIGINT, 
            username TEXT, 
            PRIMARY KEY(room_id, user)
        )""")
        await db.commit()

@asynccontextmanager
async def connect_db():
    db = await aiosqlite.connect(DB_PATH)
    try:
        yield db
    finally:
        await db.close()