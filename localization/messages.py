"""
Поддержка сообщений на двух языках
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

#Предпочтения языка от пользователя(сохраняем для базы данных)
user_languages = {}

MESSAGES = {
    "ru": {
        #Базовые сообщения
        "welcome": "👋 Добро пожаловать, {name}!\n\nЯ бот для управления задачами с мотивирующими цитатами. Используйте команды или кнопки ниже для навигации.",
        "help": "🤖 Доступные команды:\n\n"
                "📋 /tasks - Просмотр ваших задач\n"
                "➕ /addtask - Добавить новую задачу\n"
                "💡 /quote - Получить мотивирующую цитату\n"
                "🌐 /language - Изменить язык\n\n"
                "🔧 Команды администратора:\n"
                "📊 /stats - Статистика бота\n"
                "📢 /broadcast - Рассылка сообщений\n"
                "🚫 /ban - Заблокировать пользователя",
        "choose_language": "🌐 Выберите язык / Choose language:",
        "language_changed": "✅ Язык изменен на русский!",
        
        #Сообщения по управлению задачами
        "your_tasks": "📋 Ваши задачи:",
        "no_tasks": "📭 У вас пока нет задач. Добавьте первую задачу!",
        "enter_task_title": "📝 Введите название задачи:",
        "enter_task_description": "📄 Введите описание задачи (или отправьте /skip чтобы пропустить):",
        "enter_task_priority": "🎯 Введите приоритет задачи:\n\n🔴 Высокий (высокий/high/3)\n🟡 Средний (средний/medium/2)\n🟢 Низкий (низкий/low/1)",
        "invalid_task_title": "❌ Название задачи не может быть пустым. Попробуйте еще раз:",
        "task_added": "✅ Задача '{title}' успешно добавлена!",
        "task_completed": "✅ Задача '{title}' выполнена!",
        "task_deleted": "🗑️ Задача '{title}' удалена!",
        "select_task_action": "📝 Выберите действие с задачей:",
        "task_management": "📝 Управление задачами",
        
        #Сообщения по получению цитат
        "loading_quote": "💭 Загружаю цитату...",
        "quote_api_error": "😞 Не удалось получить цитату. API недоступен.",
        "quote_fetch_error": "❌ Ошибка при получении цитаты. Попробуйте позже.",
        
        #Сообщения для админа
        "bot_statistics": "📊 Статистика бота:\n\n"
                         "👥 Всего пользователей: {total_users}\n"
                         "📋 Всего задач: {total_tasks}\n"
                         "✅ Выполненных задач: {completed_tasks}\n"
                         "🟢 Активных пользователей сегодня: {active_users}",
        "enter_broadcast_message": "📢 Введите сообщение для рассылки:",
        "broadcast_results": "📊 Результаты рассылки:\n\n"
                           "✅ Успешно отправлено: {successful}\n"
                           "❌ Ошибок: {failed}\n"
                           "👥 Всего пользователей: {total}",
        "enter_user_id_to_ban": "🚫 Введите ID пользователя для блокировки:",
        "enter_user_id_to_unban": "✅ Введите ID пользователя для разблокировки:",
        "invalid_user_id": "❌ Неверный ID пользователя. Введите числовой ID:",
        "user_not_found": "❌ Пользователь не найден.",
        "user_banned": "🚫 Пользователь {user_id} ({username}) заблокирован.",
        "user_unbanned": "✅ Пользователь {user_id} ({username}) разблокирован.",
        "admin_panel": "🔧 Панель администратора",
        
        #Кнопки
        "btn_my_tasks": "📋 Мои задачи",
        "btn_add_task": "➕ Добавить задачу",
        "btn_get_quote": "💡 Получить цитату",
        "btn_language": "🌐 Язык",
        "btn_manage_tasks": "📝 Управление задачами",
        "btn_admin_panel": "🔧 Админ панель",
        "btn_complete_task": "✅ Выполнить",
        "btn_delete_task": "🗑️ Удалить",
        "btn_back": "🔙 Назад",
        "btn_view_tasks": "👁️ Просмотр задач",
    },
    
    "en": {
        #Базовые сообщения
        "welcome": "👋 Welcome, {name}!\n\nI'm a task management bot with motivational quotes. Use commands or buttons below to navigate.",
        "help": "🤖 Available commands:\n\n"
                "📋 /tasks - View your tasks\n"
                "➕ /addtask - Add new task\n"
                "💡 /quote - Get motivational quote\n"
                "🌐 /language - Change language\n\n"
                "🔧 Admin commands:\n"
                "📊 /stats - Bot statistics\n"
                "📢 /broadcast - Broadcast messages\n"
                "🚫 /ban - Ban user",
        "choose_language": "🌐 Choose language / Выберите язык:",
        "language_changed": "✅ Language changed to English!",
        
        #Сообщения по управлению задачами
        "your_tasks": "📋 Your tasks:",
        "no_tasks": "📭 You have no tasks yet. Add your first task!",
        "enter_task_title": "📝 Enter task title:",
        "enter_task_description": "📄 Enter task description (or send /skip to skip):",
        "enter_task_priority": "🎯 Enter task priority:\n\n🔴 High (high/3)\n🟡 Medium (medium/2)\n🟢 Low (low/1)",
        "invalid_task_title": "❌ Task title cannot be empty. Try again:",
        "task_added": "✅ Task '{title}' successfully added!",
        "task_completed": "✅ Task '{title}' completed!",
        "task_deleted": "🗑️ Task '{title}' deleted!",
        "select_task_action": "📝 Select task action:",
        "task_management": "📝 Task Management",
        
        #Сообщения по получению цитат
        "loading_quote": "💭 Loading quote...",
        "quote_api_error": "😞 Failed to get quote. API is unavailable.",
        "quote_fetch_error": "❌ Error fetching quote. Please try again later.",
        
        #Сообщения для адимина
        "bot_statistics": "📊 Bot Statistics:\n\n"
                         "👥 Total users: {total_users}\n"
                         "📋 Total tasks: {total_tasks}\n"
                         "✅ Completed tasks: {completed_tasks}\n"
                         "🟢 Active users today: {active_users}",
        "enter_broadcast_message": "📢 Enter broadcast message:",
        "broadcast_results": "📊 Broadcast Results:\n\n"
                           "✅ Successfully sent: {successful}\n"
                           "❌ Errors: {failed}\n"
                           "👥 Total users: {total}",
        "enter_user_id_to_ban": "🚫 Enter user ID to ban:",
        "enter_user_id_to_unban": "✅ Enter user ID to unban:",
        "invalid_user_id": "❌ Invalid user ID. Enter numeric ID:",
        "user_not_found": "❌ User not found.",
        "user_banned": "🚫 User {user_id} ({username}) has been banned.",
        "user_unbanned": "✅ User {user_id} ({username}) has been unbanned.",
        "admin_panel": "🔧 Admin Panel",
        
        #Кнопки
        "btn_my_tasks": "📋 My Tasks",
        "btn_add_task": "➕ Add Task",
        "btn_get_quote": "💡 Get Quote",
        "btn_language": "🌐 Language",
        "btn_manage_tasks": "📝 Manage Tasks",
        "btn_admin_panel": "🔧 Admin Panel",
        "btn_complete_task": "✅ Complete",
        "btn_delete_task": "🗑️ Delete",
        "btn_back": "🔙 Back",
        "btn_view_tasks": "👁️ View Tasks",
    }
}


def get_message(key: str, language: str = "ru") -> str:
    """Получаем сообщение на соответствующем языке по ключу"""
    if language not in MESSAGES:
        language = "ru"  #Возвращаемся к русскому языку
    
    if key not in MESSAGES[language]:
        logger.warning(f"Message key '{key}' not found for language '{language}'")
        return f"[{key}]"
    
    return MESSAGES[language][key]


def set_user_language(user_id: int, language: str):
    """Устанавливаем язык для пользователя"""
    if language in MESSAGES:
        user_languages[user_id] = language
        logger.info(f"User {user_id} language set to {language}")
    else:
        logger.warning(f"Attempted to set invalid language '{language}' for user {user_id}")


def get_user_language(user_id: int) -> str:
    """Получаем язык пользователя"""
    return user_languages.get(user_id, "ru")  #язык по умолчанию русский



