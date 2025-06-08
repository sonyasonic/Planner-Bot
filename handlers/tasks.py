"""
Обработка команд для создания задач и управления ими
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from localization.messages import get_message, get_user_language
from utils.keyboards import get_tasks_keyboard, get_task_actions_keyboard
from storage.database import Database
from states.task_states import TaskStates

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("tasks"))
async def view_tasks_handler(message: Message):
    """Обработка команды /tasks, которая показывает все задачи пользователя"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    db = Database()
    tasks = await db.get_user_tasks(user_id)
    
    if not tasks:
        text = get_message("no_tasks", lang)
        await message.answer(text, reply_markup=get_tasks_keyboard(lang))
        return
    
    #Форматируем
    tasks_text = get_message("your_tasks", lang) + "\n\n"
    for i, task in enumerate(tasks, 1):
        status = "✅" if task["completed"] else "⭕"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
        tasks_text += f"{i}. {status} {priority_emoji} {task['title']}\n"
        if task["description"]:
            tasks_text += f"   📝 {task['description']}\n"
        tasks_text += f"   📅 {task['created_at']}\n\n"
    
    await message.answer(
        tasks_text,
        reply_markup=get_tasks_keyboard(lang, len(tasks) > 0)
    )
    
    logger.info(f"User {user_id} viewed {len(tasks)} tasks")


@router.message(Command("addtask"))
async def add_task_command(message: Message, state: FSMContext):
    """Обработка команды /addtask, которая добавляет новую задачу"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    text = get_message("enter_task_title", lang)
    await message.answer(text)
    await state.set_state(TaskStates.waiting_for_title)
    
    logger.info(f"User {user_id} started adding new task")


@router.message(F.text.in_(["➕ Добавить задачу", "➕ Add Task"]))
async def add_task_button(message: Message, state: FSMContext):
    """Обработка кнопок клавиатуры, которая отвечает за добавление задачи"""
    await add_task_command(message, state)


@router.message(TaskStates.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    """Название задачи"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    title = message.text.strip()
    if not title:
        text = get_message("invalid_task_title", lang)
        await message.answer(text)
        return
    
    #Сохраняем данные
    await state.update_data(title=title)
    
    #Просим описание задачи пользователя
    text = get_message("enter_task_description", lang)
    await message.answer(text)
    await state.set_state(TaskStates.waiting_for_description)
    
    logger.info(f"User {user_id} entered task title: {title}")


@router.message(TaskStates.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext):
    """Описание задачи"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    description = message.text.strip()
    
    #Сохраняем описание
    await state.update_data(description=description)
    
    #Запрашиваем у пользователя приоритетность задачи
    text = get_message("enter_task_priority", lang)
    await message.answer(text)
    await state.set_state(TaskStates.waiting_for_priority)
    
    logger.info(f"User {user_id} entered task description")


@router.message(TaskStates.waiting_for_priority)
async def process_task_priority(message: Message, state: FSMContext):
    """Приоритетность задачи"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    priority_text = message.text.strip().lower()
    
    #Просим выбрать что-то из выпадающего списка
    priority_map = {
        "низкий": "low", "low": "low", "1": "low",
        "средний": "medium", "medium": "medium", "2": "medium", 
        "высокий": "high", "high": "high", "3": "high"
    }
    
    priority = priority_map.get(priority_text, "medium")
    
    #Получаем данные
    data = await state.get_data()
    title = data.get("title")
    description = data.get("description", "")
    
    #Создаем задачу целиком
    db = Database()
    task_id = await db.add_task(user_id, title, description, priority)

    await state.clear()
    
    #Отправляем уведомление о созданной задаче
    text = get_message("task_added", lang).format(title=title)
    await message.answer(text, reply_markup=get_tasks_keyboard(lang, True))
    
    logger.info(f"User {user_id} added task {task_id}: {title} with priority {priority}")


@router.callback_query(F.data == "view_tasks")
async def view_tasks_callback(callback: CallbackQuery):
    """Обрабатываем callback"""
    await view_tasks_handler(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("task_"))
async def task_action_callback(callback: CallbackQuery):
    """Обрабатываем callback, связанный с обработкой задач"""
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    data_parts = callback.data.split("_")
    
    if len(data_parts) < 2:
        await callback.answer()
        return
    
    action = data_parts[1]
    
    db = Database()
    tasks = await db.get_user_tasks(user_id)
    
    if action == "list":
        #Показываем список задач
        if not tasks:
            text = get_message("no_tasks", lang)
            await callback.message.edit_text(text)
            await callback.answer()
            return
        
        text = get_message("select_task_action", lang)
        keyboard = get_task_actions_keyboard(tasks, lang)
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    elif action == "complete" and len(data_parts) >= 3:
        #Пользователь выполняет задачу
        try:
            task_index = int(data_parts[2]) - 1
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                await db.update_task_status(task["id"], True)
                text = get_message("task_completed", lang).format(title=task["title"])
                await callback.message.edit_text(text)
                logger.info(f"User {user_id} completed task {task['id']}")
            else:
                await callback.answer("Task not found")
        except (ValueError, IndexError):
            await callback.answer("Invalid task number")
    
    elif action == "delete" and len(data_parts) >= 3:
        #Пользователь удаляет задачу
        try:
            task_index = int(data_parts[2]) - 1
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                await db.delete_task(task["id"])
                text = get_message("task_deleted", lang).format(title=task["title"])
                await callback.message.edit_text(text)
                logger.info(f"User {user_id} deleted task {task['id']}")
            else:
                await callback.answer("Task not found")
        except (ValueError, IndexError):
            await callback.answer("Invalid task number")
    
    await callback.answer()


@router.message(F.text.in_(["📝 Управление задачами", "📝 Manage Tasks"]))
async def manage_tasks_button(message: Message):
    """Обработка кнопок клавиатуры, связанных с управлениеми задачами"""
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    text = get_message("task_management", lang)
    await message.answer(text, reply_markup=get_tasks_keyboard(lang))
