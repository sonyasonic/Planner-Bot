"""
Обработчик базовых команд бота (/start, /help, /language)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from localization.messages import get_message, set_user_language, get_user_language
from utils.keyboards import get_language_keyboard, get_main_keyboard
from storage.database import Database

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message):
    """обработка команды /start """
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    #Инициализируем пользователя в базе данных
    db = Database()
    await db.add_user(user_id, username)
    
    lang = get_user_language(user_id)
    welcome_text = get_message("welcome", lang).format(
        name=message.from_user.first_name or "User"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(lang)
    )
    
    logger.info(f"User {user_id} ({username}) started the bot")


@router.message(Command("help"))
async def help_handler(message: Message):
    """Обработка команды /help """
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    help_text = get_message("help", lang)
    await message.answer(help_text)
    
    logger.info(f"User {user_id} requested help")


@router.message(Command("language"))
async def language_handler(message: Message):
    """Обработка команды /language, которая отвечает за язык бота"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    text = get_message("choose_language", lang)
    await message.answer(text, reply_markup=get_language_keyboard())
    
    logger.info(f"User {user_id} opened language selection")


@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery):
    """Обработка команды, отвечающей за выбор языка"""
    user_id = callback.from_user.id
    selected_lang = callback.data.split("_")[1]
    
    #Установленный язык пользователя
    set_user_language(user_id, selected_lang)
    
    #Подтверждение
    text = get_message("language_changed", selected_lang)
    await callback.message.edit_text(text)
    
    #Новое приветственное сообщение с клавиатурой, но на другом языке
    await callback.message.answer(
        get_message("welcome", selected_lang).format(
            name=callback.from_user.first_name or "User"
        ),
        reply_markup=get_main_keyboard(selected_lang)
    )
    
    await callback.answer()
    logger.info(f"User {user_id} changed language to {selected_lang}")


@router.message(F.text.in_(["📋 Мои задачи", "📋 My Tasks"]))
async def tasks_button_handler(message: Message):
    """Обработка кнопок клавиатуры для установки задач"""
    from handlers.tasks import view_tasks_handler
    await view_tasks_handler(message)


@router.message(F.text.in_(["💡 Получить цитату", "💡 Get Quote"]))
async def quote_button_handler(message: Message):
    """Обработка кнопок клавиатуры для получения цитаты"""
    from handlers.quotes import quote_handler
    await quote_handler(message)


@router.message(F.text.in_(["🌐 Язык", "🌐 Language"]))
async def language_button_handler(message: Message):
    """Обработка кнопок клавиатуры,которые отвечают за смену языка"""
    await language_handler(message)
