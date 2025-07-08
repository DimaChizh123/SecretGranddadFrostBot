from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError


async def notify_admin(message: str, admin_id: int, bot: Bot, room_name: str, user_id: int) -> None:
    try:
        if admin_id != user_id:
            await bot.send_message(chat_id=admin_id, text=f"Комната {room_name}: {message}")
    except TelegramForbiddenError:
        pass