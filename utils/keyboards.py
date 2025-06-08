"""
Инлайн и реплай клавиатуры для бота
"""
from typing import List, Dict, Any
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

from localization.messages import get_message
from config import Config


def get_main_keyboard(language: str = "ru") -> ReplyKeyboardMarkup:
    """Клавиатура меню"""
    config = Config()
    
    keyboard = [
        [
            KeyboardButton(text=get_message("btn_my_tasks", language)),
            KeyboardButton(text=get_message("btn_add_task", language))
        ],
        [
            KeyboardButton(text=get_message("btn_get_quote", language)),
            KeyboardButton(text=get_message("btn_language", language))
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора языка"""
    keyboard = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tasks_keyboard(language: str = "ru", has_tasks: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для создания задач"""
    keyboard = []

    keyboard.append([
        InlineKeyboardButton(
            text=get_message("btn_add_task", language),
            callback_data="add_task"
        )
    ])

    if has_tasks:
        keyboard.append([
            InlineKeyboardButton(
                text=get_message("btn_manage_tasks", language),
                callback_data="task_list"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_actions_keyboard(tasks: List[Dict[str, Any]], language: str = "ru") -> InlineKeyboardMarkup:
    """Управление задачами"""
    keyboard = []
    
    for i, task in enumerate(tasks[:10], 1):
        status_emoji = "✅" if task["completed"] else "⭕"
        task_title = task["title"][:20] + "..." if len(task["title"]) > 20 else task["title"]

        row = []
        
        if not task["completed"]:
            row.append(InlineKeyboardButton(
                text=f"{status_emoji} {task_title}",
                callback_data=f"task_complete_{i}"
            ))
        else:
            row.append(InlineKeyboardButton(
                text=f"{status_emoji} {task_title}",
                callback_data="task_already_completed"
            ))
        
        row.append(InlineKeyboardButton(
            text="🗑️",
            callback_data=f"task_delete_{i}"
        ))
        
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            text=get_message("btn_back", language),
            callback_data="back_to_tasks"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для админских функций"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📊 Statistics", 
                callback_data="admin_stats"
            ),
            InlineKeyboardButton(
                text="📢 Broadcast", 
                callback_data="admin_broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 Ban User", 
                callback_data="admin_ban"
            ),
            InlineKeyboardButton(
                text="✅ Unban User", 
                callback_data="admin_unban"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 User List", 
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="📋 All Tasks", 
                callback_data="admin_tasks"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_confirm_keyboard(action: str, task_id: str, language: str = "ru") -> InlineKeyboardMarkup:
    """Кнопки клавиатуры для подтверждения действий"""
    if action == "delete":
        confirm_text = "🗑️ Confirm Delete" if language == "en" else "🗑️ Подтвердить удаление"
        cancel_text = "❌ Cancel" if language == "en" else "❌ Отмена"
    elif action == "complete":
        confirm_text = "✅ Mark Complete" if language == "en" else "✅ Отметить выполненной"
        cancel_text = "❌ Cancel" if language == "en" else "❌ Отмена"
    else:
        confirm_text = "✅ Confirm" if language == "en" else "✅ Подтвердить"
        cancel_text = "❌ Cancel" if language == "en" else "❌ Отмена"
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=confirm_text,
                callback_data=f"confirm_{action}_{task_id}"
            ),
            InlineKeyboardButton(
                text=cancel_text,
                callback_data="cancel_action"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
