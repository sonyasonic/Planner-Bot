"""
Хэндлер для цитат
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from localization.messages import get_message, get_user_language
from services.quotes_api import QuotesAPI

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("quote"))
async def quote_handler(message: Message):
    """Обработка команды /quote, которая отвечает за получение мотивирующей цитаты"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    #Сообщение о загрузке
    loading_msg = await message.answer(get_message("loading_quote", lang))
    
    try:
        #Получаем цитату через API
        quotes_api = QuotesAPI()
        quote_data = await quotes_api.get_random_quote()
        
        if quote_data:
            #Форматирование сообщения
            quote_text = f"💭 \"{quote_data['text']}\"\n\n— {quote_data['author']}"
            
            #Меняем сообщение о загрузке на сообщение с цитатой
            await loading_msg.edit_text(quote_text)
            
            logger.info(f"User {user_id} received quote from {quote_data['author']}")
        else:
            #Если с API нет данных
            error_text = get_message("quote_api_error", lang)
            await loading_msg.edit_text(error_text)
            logger.warning(f"No quote data received for user {user_id}")
            
    except Exception as e:
        error_text = get_message("quote_fetch_error", lang)
        await loading_msg.edit_text(error_text)
        logger.error(f"Error fetching quote for user {user_id}: {e}")


@router.message(F.text.in_(["💡 Получить цитату", "💡 Get Quote"]))
async def quote_button_handler(message: Message):
    """Обработка кнопок клавиатуры для получения цитаты"""
    await quote_handler(message)


@router.message(F.text.in_(["🔄 Новая цитата", "🔄 New Quote"]))
async def new_quote_handler(message: Message):
    """Обработка команды для получения новой цитаты"""
    await quote_handler(message)
