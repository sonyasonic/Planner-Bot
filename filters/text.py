"""
Фильтры, связанные с текстом сообщений, для обработки самих сообщений
"""

import logging
from typing import Union, List
from aiogram.filters import BaseFilter
from aiogram.types import Message

logger = logging.getLogger(__name__)


class TextFilter(BaseFilter):
    """Фильтр для сообщений по их содержанию"""
    
    def __init__(self, text: Union[str, List[str]], ignore_case: bool = True):
        """
        Инициализируем фильтр, который принимает и обрабатывает сообщения
        
        Аргументы:
            текст(text): строка(string) или список(list of strings)
            ignore_case: игнорируем регистр текста
        """
        if isinstance(text, str):
            self.texts = [text]
        else:
            self.texts = text
        
        self.ignore_case = ignore_case
        
        if self.ignore_case:
            self.texts = [t.lower() for t in self.texts]
    
    async def __call__(self, message: Message) -> bool:
        """Проверяем, соответствует ли сообщение фильтрам"""
        if not message.text:
            return False
        
        message_text = message.text
        if self.ignore_case:
            message_text = message_text.lower()
        
        return message_text in self.texts


class CommandFilter(BaseFilter):
    """Фильтр для специальных команд бота"""
    
    def __init__(self, commands: Union[str, List[str]], include_args: bool = False):
        """
        Инициализируем фильтр для обработки команд
        
        Аргументы:
            команды(commands): команда(command) или список команд(list of commands) (без /)
            проверка аргументов(include_args): проверяем аргументы команд на соответсвие
        """
        if isinstance(commands, str):
            self.commands = [commands]
        else:
            self.commands = commands
        
        #Проверяем, что команда начинается с символа /
        self.commands = ['/' + cmd.lstrip('/') for cmd in self.commands]
        self.include_args = include_args
    
    async def __call__(self, message: Message) -> bool:
        """Проверяем, является ли сообщение одной из специальных команд"""
        if not message.text or not message.text.startswith('/'):
            return False
        
        if self.include_args:
            #Проверяем на соответствие всю команду с аргументами
            return any(message.text.startswith(cmd) for cmd in self.commands)
        else:
            #Соединяем только команду(первое слово), т.к. соответствует только оно
            command = message.text.split()[0]
            return command in self.commands



