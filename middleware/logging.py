"""
Отслеживаем активность бота
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from storage.database import Database

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Обработка и загрузка в базу данных по активности бота"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Время работы и детали выполнения"""
        
        start_time = datetime.now()
        user_id = event.from_user.id
        username = event.from_user.username or "Unknown"

        if isinstance(event, Message):
            event_type = "message"
            event_data = {
                "text": event.text[:100] if event.text else None,
                "content_type": event.content_type,
                "chat_type": event.chat.type
            }
        elif isinstance(event, CallbackQuery):
            event_type = "callback"
            event_data = {
                "data": event.data,
                "message_id": event.message.message_id if event.message else None
            }
        else:
            event_type = "unknown"
            event_data = {}
        
        logger.info(f"[{event_type.upper()}] User {user_id} ({username}): {event_data}")
        
        #Статистика бота
        db = Database()
        await db.update_statistics("total_requests")
        
        try:
            result = await handler(event, data)

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            logger.info(f"[SUCCESS] Processed {event_type} from user {user_id} "
                       f"in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            #Обработка оишбок при запросе
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            logger.error(f"[ERROR] Failed to process {event_type} from user {user_id} "
                        f"after {processing_time:.3f}s: {e}")
            
            #Сообщение об оишбке для пользователя
            error_message = ("😞 К сожалению, произошла ошибка при попытке обработать ваш запрос.\n"
                           "😞 Unfortunately an error occurred while processing your request.")
            
            try:
                if isinstance(event, Message):
                    await event.answer(error_message)
                elif isinstance(event, CallbackQuery):
                    await event.answer("Произошла ошибка / Error occurred", show_alert=True)
            except:
                logger.error(f"Failed to send error message to user {user_id}")

            raise


class CommandLoggerMiddleware(BaseMiddleware):
    """Мидлвари для обработки запросов по командам"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        #Обработка сообщений с командами
        if not event.text or not event.text.startswith('/'):
            return await handler(event, data)
        
        command = event.text.split()[0].lower()
        user_id = event.from_user.id

        logger.info(f"Command usage: {command} by user {user_id}")
        
        #Статистика
        db = Database()
        stat_name = f"command_{command.replace('/', '')}_usage"
        await db.update_statistics(stat_name)
        
        return await handler(event, data)
