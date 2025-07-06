import logging
import random

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link

from app.db.rooms import get_room_name_id
from app.db.core import connect_db
from app.utils.notifiers import notify_admin

logger = logging.getLogger(__name__)

async def add_user(code: int, user_id: int, username: str, bot: Bot) -> str:
    async with connect_db() as db:
        room_cursor = await db.execute("SELECT id, admin, name FROM rooms WHERE code = ?", (code,))
        room_row = await room_cursor.fetchone()
        if not room_row:
            return "Ошибка! Комната не найдена"
        room_id, admin_id, room_name = room_row
        username_cursor = await db.execute("SELECT username FROM users WHERE room_id = ?", (room_id,))
        usernames_row = await username_cursor.fetchall()
        usernames = [user[0] for user in usernames_row]
        if username in usernames:
            return "Ошибка! В комнате уже есть участник с таким именем"
        user_cursor = await db.execute("SELECT room_id, user, username FROM users WHERE user = ? AND room_id = ?", (user_id, room_id))
        await db.execute(
            "INSERT INTO users (room_id, user, username) VALUES (?, ?, ?) ON CONFLICT (room_id, user) DO UPDATE SET username = excluded.username",
            (room_id, user_id, username))
        await db.commit()
        old_user = await user_cursor.fetchone()
        if not old_user:
            await notify_admin(f"В комнату добавлен участник {username}", admin_id, bot, room_name, user_id)
            logger.info(f"Пользователь добавлен: {user_id} ({username})")
            return "Вы были успешно добавлены в комнату!"
        else:
            old_username = old_user[2]
            await notify_admin(f"Участник {old_username} изменил имя на {username}", admin_id, bot, room_name, user_id)
            logger.info(f"Пользователь изменён: {user_id} ({old_username} -> {username})")
            return "Ваши данные были обновлены!"

async def get_users_list(room_id: int) -> list[tuple[int, str]]:
    async with connect_db() as db:
        admin_cursor = await db.execute("SELECT user, username FROM rooms JOIN users ON rooms.id = users.room_id WHERE id = ? AND admin = user", (room_id,))
        admin = await admin_cursor.fetchone()
        if not admin:
            return []
        admin_id, admin_name = admin
        user_cursor = await db.execute("SELECT user, username FROM users WHERE room_id = ? AND user != ?", (room_id, admin_id))
        users = [(u[0], u[1]) for u in await user_cursor.fetchall()]
        return [(admin_id, admin_name)] + users

async def show_room(room_id: int, user_id: int, bot: Bot) -> tuple[str, bool]:
    room = await get_room_name_id(room_id)
    if not room:
        return "Ошибка! Такая комната не найдена", False
    async with connect_db() as db:
        cursor = await db.execute("SELECT user FROM users WHERE room_id = ? AND user = ?", (room_id, user_id))
        if not await cursor.fetchone():
            return "Ошибка! Скорее всего вас исключили из этой комнаты", False
    link = await create_start_link(bot, str(room[1]))
    users = await get_users_list(room_id)
    if not users:
        return "Ошибка! Комната пуста или недоступна", False
    result = f"{room[0]} (код: {room[1]})\nСсылка: {link}\nСписок участников:\n"
    for i, (_, name) in enumerate(users):
        result += f"{'⭐️ ' if i == 0 else '👤 '}{name}\n"
    return result, True

async def get_rooms(user_id: int) -> list[list[tuple[int, str]]]:
    async with connect_db() as db:
        rooms_cursor = await db.execute("SELECT id, name FROM rooms WHERE admin = ?", (user_id,))
        admin_rooms = [(room[0], room[1]) for room in await rooms_cursor.fetchall()]
        users_cursor = await db.execute("SELECT id, name FROM users JOIN rooms ON users.room_id = rooms.id WHERE user = ? AND room_id NOT IN (SELECT id FROM rooms WHERE admin = ?)", (user_id, user_id))
        guest_rooms = [(user[0], user[1]) for user in await users_cursor.fetchall()]
        return [admin_rooms, guest_rooms]

async def remove_user_from_db(user_id: int, room_id: int, bot: Bot) -> None:
    async with connect_db() as db:
        room_cursor = await db.execute("SELECT admin, name FROM rooms WHERE id = ?", (room_id,))
        room_row = await room_cursor.fetchone()
        if not room_row:
            return
        admin_id, room_name = room_row
        user_cursor = await db.execute("SELECT username FROM users WHERE user = ? AND room_id = ?", (user_id, room_id))
        username = await user_cursor.fetchone()
        if not username:
            return
        await notify_admin(f"Участник {username[0]} был удалён из комнаты", admin_id, bot, room_name, user_id)
        await db.execute("DELETE FROM users WHERE user = ? AND room_id = ?", (user_id, room_id))
        await db.commit()
        logger.info(f"Пользователь удалён: {user_id} ({username})")

async def shuffle_names(original: list[str]) -> list[str]:
    while True:
        shuffled = original[:]
        random.shuffle(shuffled)
        if all(shuffled[i] != original[i] for i in range(len(original))):
            return shuffled