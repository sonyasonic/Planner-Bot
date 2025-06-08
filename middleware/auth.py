"""
Авторизация и аутентификация
"""
import logging
from typing import Callable, Dict, Any, Awaitable, List
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from storage.database import Database

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """пользовательская авторизация и аутентификация"""
    
    def __init__(self, admin_ids: List[int]):
        super().__init__()
        self.admin_ids = admin_ids
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Аутентификация"""
        
        user_id = event.from_user.id
        db = Database()
        
        #Проверяем, заблокирован ли пользователь
        if await db.is_user_banned(user_id):
            logger.warning(f"Banned user {user_id} attempted to use bot")
            
            #Отправляем уведомление о блокировке
            if isinstance(event, Message):
                await event.answer("🚫 Вы заблокированы и не можете использовать этого бота.\n"
                                 "🚫 You are banned and cannot use this bot.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Вы заблокированы / You are banned", show_alert=True)
            
            return
        
        #добавляем информацию о пользователе в базу
        data["user_id"] = user_id
        data["is_admin"] = user_id in self.admin_ids
        
        #Регистрируем активность пользователя
        username = event.from_user.username
        await db.add_user(user_id, username)

        if isinstance(event, Message):
            logger.info(f"User {user_id} ({username}) sent message: {event.text[:50]}...")
        elif isinstance(event, CallbackQuery):
            logger.info(f"User {user_id} ({username}) pressed button: {event.data}")

        return await handler(event, data)


class AdminOnlyMiddleware(BaseMiddleware):
    """Мидлвари для админов"""
    
    def __init__(self, admin_ids: List[int]):
        super().__init__()
        self.admin_ids = admin_ids
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Проверяем, является ли пользователь админом"""
        
        user_id = event.from_user.id
        
        if user_id not in self.admin_ids:
            logger.warning(f"Non-admin user {user_id} tried to access admin function")
            
            #Уведомляем о том, что у пользователя нет прав доступа
            if isinstance(event, Message):
                await event.answer("🔒 У вас нет разрешения к этой команде.\n"
                                 "🔒 You don't have permission to use this command.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🔒 Доступ запрещен / Access denied", show_alert=True)
            
            return
        
        #Если пользователь админ, то продолжаем
        data["is_admin"] = True
        return await handler(event, data)
