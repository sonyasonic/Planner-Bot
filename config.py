"""
Конфиг для управления ботом
"""
import os
from dotenv import load_dotenv

#Загружаем данные из .env файла(есть образец по заполнению .env.example)
load_dotenv()


class Config:
    """Управление настройками бота"""
    
    def __init__(self):
        #Токен
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in environment variables")
        
        #Админ ID
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip().isdigit()]
        
        #API
        self.ZENQUOTES_API_URL = os.getenv("ZENQUOTES_API_URL", "https://zenquotes.io/api/random")
        
        #Кэш
        self.CACHE_DURATION = int(os.getenv("CACHE_DURATION", "3600"))
        
        #Логирование
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "bot.log")
        
        #База данных
        self.DATABASE_FILE = os.getenv("DATABASE_FILE", "data/database.json")
        
        #Проверяем директорию
        os.makedirs(os.path.dirname(self.DATABASE_FILE), exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def is_admin(self, user_id: int) -> bool:
        """Проверяем, является ли пользователь админом"""
        return user_id in self.ADMIN_IDS
