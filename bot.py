"""
Основной файл для бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from handlers import basic, tasks, admin, quotes
from middleware.logging import LoggingMiddleware
from middleware.auth import AuthMiddleware
from storage.database import Database


async def main():
    """Main функция"""
    config = Config()
    #Логирование
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Task Management Bot...")
    
    #База данных
    db = Database(config.DATABASE_FILE)
    await db.initialize()
    
    #Бот и диспетсчер
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    #Мидлвари
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(AuthMiddleware(config.ADMIN_IDS))
    dp.callback_query.middleware(AuthMiddleware(config.ADMIN_IDS))
    
    #Роутеры
    dp.include_router(basic.router)
    dp.include_router(tasks.router)
    dp.include_router(quotes.router)
    dp.include_router(admin.router)

    #Запуск бота
    try:
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
