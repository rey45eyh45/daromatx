import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from handlers import start, courses, profile, admin, payments
from database.base import init_db

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    """Bot ishga tushirish"""
    
    # Database yaratish
    await init_db()
    
    # Bot yaratish
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Dispatcher yaratish
    dp = Dispatcher()
    
    # Handlerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(courses.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    dp.include_router(payments.router)
    
    logger.info("Bot ishga tushdi!")
    
    # Polling boshlash
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
