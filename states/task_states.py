"""
FSM состояния
"""
from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    """Состояния по обработке и созданию задач пользователем"""
    
    #создание задач
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_priority = State()
    
    #редактирование задач
    selecting_task_to_edit = State()
    editing_task_title = State()
    editing_task_description = State()
    
    #выполнение задач
    selecting_task_to_complete = State()
    confirming_task_completion = State()
    
    #удаление задач
    selecting_task_to_delete = State()
    confirming_task_deletion = State()


class AdminStates(StatesGroup):
    """Состояния админских команд и действий"""
    
    #транслирование сообщений всем пользователям
    waiting_for_broadcast = State()
    confirming_broadcast = State()
    
    #управление пользователями
    waiting_for_ban_user_id = State()
    confirming_ban = State()
    waiting_for_unban_user_id = State()
    confirming_unban = State()
    
    #статистика
    viewing_detailed_stats = State()
    exporting_data = State()


class LanguageStates(StatesGroup):
    """Выбор языка(обработка состояний)"""
    
    selecting_language = State()
    confirming_language_change = State()

