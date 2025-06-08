"""
Инициализация для пакета с клавиатурой
"""
from .keyboards import (
    get_main_keyboard,
    get_tasks_keyboard,
    get_language_keyboard,
    get_admin_keyboard,
    get_task_actions_keyboard,
    get_task_confirm_keyboard

)

__all__ = [
    'get_main_keyboard',
    'get_tasks_keyboard', 
    'get_language_keyboard',
    'get_admin_keyboard',
    'get_task_actions_keyboard',
    'get_task_confirm_keyboard'
]
