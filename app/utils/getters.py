from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError


async def get_tg_username(bot: Bot, user_id: int) -> str | None:
    try:
        chat = await bot.get_chat(user_id)
        return f"@{chat.username}" if chat.username else ""
    except TelegramForbiddenError:
        return None