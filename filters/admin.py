"""
Фильтры, связанные с командами админа
"""
import logging
from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import Config

logger = logging.getLogger(__name__)


class AdminFilter(BaseFilter):
    """Фильтр, который разрешает админ-команды только админам"""
    
    def __init__(self):
        self.config = Config()
        self.admin_ids = self.config.ADMIN_IDS
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Проверяем, является ли пользователь админом"""
        user_id = event.from_user.id
        is_admin = user_id in self.admin_ids
        
        if not is_admin:
            logger.warning(f"Non-admin user {user_id} tried to access admin function")
            
            #Сообщение об отсутствии прав доступа
            access_denied_text = (
                "🔒 У вас нет прав доступа к этой команде.\n"
                "🔒 You don't have permission to use this command."
            )
            
            try:
                if isinstance(event, Message):
                    await event.answer(access_denied_text)
                elif isinstance(event, CallbackQuery):
                    await event.answer("🔒 Доступ запрещен / Access denied", show_alert=True)
            except Exception as e:
                logger.error(f"Error sending access denied message: {e}")
        
        return is_admin

