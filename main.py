import asyncio
from aiogram import Bot, Dispatcher

from app.db.core import init_db
from app.handlers import routers
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO, format = "%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def main():
    load_dotenv(dotenv_path="app/config.env")
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        logger.critical("BOT_TOKEN не найден")
        exit(1)

    try:
        await init_db()
        logger.info("БД успешно инициализирована")
    except Exception as e:
        logger.exception(f"Ошибка при инициализации БД: {e}")
        exit(1)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    for router in routers:
        dp.include_router(router)

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Сессия закрыта")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Завершение работы")
    except Exception as e:
        logger.exception(f"Фатальная ошибка: {e}")