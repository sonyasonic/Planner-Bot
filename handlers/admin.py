"""
Обработчик(хэндлер) для админской панели
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from localization.messages import get_message, get_user_language
from utils.keyboards import get_admin_keyboard
from storage.database import Database
from states.task_states import AdminStates
from filters.admin import AdminFilter

router = Router()
logger = logging.getLogger(__name__)

#Применяем админ-фильтр для всех обработчиков-хэндлеров в этом роутере
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.message(Command("stats"))
async def stats_handler(message: Message):
    """Обрабатываем команду /stats, которая показывает статистику бота"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    db = Database()
    stats = await db.get_statistics()
    
    stats_text = get_message("bot_statistics", lang).format(
        total_users=stats["total_users"],
        total_tasks=stats["total_tasks"],
        completed_tasks=stats["completed_tasks"],
        active_users=stats["active_users_today"]
    )
    
    await message.answer(stats_text, reply_markup=get_admin_keyboard(lang))
    logger.info(f"Admin {user_id} viewed bot statistics")


@router.message(Command("broadcast"))
async def broadcast_handler(message: Message, state: FSMContext):
    """Обрабатываем команду /broadcast, которая отправляет сообщение всем пользователям"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    text = get_message("enter_broadcast_message", lang)
    await message.answer(text)
    await state.set_state(AdminStates.waiting_for_broadcast)
    
    logger.info(f"Admin {user_id} started broadcast")


@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обрабатываем сообщение, которое транслируется пользователям"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    broadcast_text = message.text
    
    db = Database()
    users = await db.get_all_users()
    
    successful = 0
    failed = 0
    
    #Отправляем сообщение всем пользователям
    for user in users:
        try:
            await message.bot.send_message(user["id"], broadcast_text)
            successful += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to send broadcast to user {user['id']}: {e}")

    await state.clear()
    
    #Отправляем сообщение
    result_text = get_message("broadcast_results", lang).format(
        successful=successful,
        failed=failed,
        total=len(users)
    )
    await message.answer(result_text)
    
    logger.info(f"Admin {user_id} sent broadcast to {successful}/{len(users)} users")


@router.message(Command("ban"))
async def ban_handler(message: Message, state: FSMContext):
    """Обработка команды /ban, которая блокирует пользователя"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    #Проверяем наличие ID
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args and args[0].isdigit():
        #Блокируем пользователя напрямую
        target_user_id = int(args[0])
        await process_ban_user(message, target_user_id)
    else:
        #Запрос на ID пользователя
        text = get_message("enter_user_id_to_ban", lang)
        await message.answer(text)
        await state.set_state(AdminStates.waiting_for_ban_user_id)
    
    logger.info(f"Admin {user_id} initiated ban process")


@router.message(AdminStates.waiting_for_ban_user_id)
async def process_ban_user_id(message: Message, state: FSMContext):
    """Обрабатываем ID пользователя для дальнейшей блокировки"""
    if not message.text.isdigit():
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        text = get_message("invalid_user_id", lang)
        await message.answer(text)
        return
    
    target_user_id = int(message.text)
    await process_ban_user(message, target_user_id)
    await state.clear()


async def process_ban_user(message: Message, target_user_id: int):
    """Блокируем пользователя"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    db = Database()
    
    #Проверяем, существует ли пользователь
    user = await db.get_user(target_user_id)
    if not user:
        text = get_message("user_not_found", lang)
        await message.answer(text)
        return
    
    #Блокировка
    await db.ban_user(target_user_id)
    
    text = get_message("user_banned", lang).format(
        user_id=target_user_id,
        username=user.get("username", "Unknown")
    )
    await message.answer(text)
    
    logger.info(f"Admin {user_id} banned user {target_user_id}")


@router.message(Command("unban"))
async def unban_handler(message: Message, state: FSMContext):
    """Обрабатываем команду /unban - разблокировку пользователя"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    #Проверяем на наличие ID
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args and args[0].isdigit():
        #Разблокировать напрямую
        target_user_id = int(args[0])
        await process_unban_user(message, target_user_id)
    else:
        #Запрашиваем ID
        text = get_message("enter_user_id_to_unban", lang)
        await message.answer(text)
        await state.set_state(AdminStates.waiting_for_unban_user_id)
    
    logger.info(f"Admin {user_id} initiated unban process")


@router.message(AdminStates.waiting_for_unban_user_id)
async def process_unban_user_id(message: Message, state: FSMContext):
    """Обрабатываем ID для разблокировки"""
    if not message.text.isdigit():
        user_id = message.from_user.id
        lang = get_user_language(user_id)
        text = get_message("invalid_user_id", lang)
        await message.answer(text)
        return
    
    target_user_id = int(message.text)
    await process_unban_user(message, target_user_id)
    await state.clear()


async def process_unban_user(message: Message, target_user_id: int):
    """Разблоикруем пользователя"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    db = Database()
    
    #Проверяем, существует ли пользователь
    user = await db.get_user(target_user_id)
    if not user:
        text = get_message("user_not_found", lang)
        await message.answer(text)
        return
    
    #Разблокируем пользователя
    await db.unban_user(target_user_id)
    
    text = get_message("user_unbanned", lang).format(
        user_id=target_user_id,
        username=user.get("username", "Unknown")
    )
    await message.answer(text)
    
    logger.info(f"Admin {user_id} unbanned user {target_user_id}")


@router.message(F.text.in_(["🔧 Админ панель", "🔧 Admin Panel"]))
async def admin_panel_button(message: Message):
    """Обработка админ-панели"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    text = get_message("admin_panel", lang)
    await message.answer(text, reply_markup=get_admin_keyboard(lang))
