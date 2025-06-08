"""
JSON база данных
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class Database:
    """JSON база данных для хранения данных по боту"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, db_file: str = "data/database.json"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.db_file = db_file
                    cls._instance.data = {
                        "users": {},
                        "tasks": {},
                        "banned_users": set(),
                        "statistics": {
                            "total_requests": 0,
                            "total_tasks_created": 0,
                            "total_quotes_requested": 0
                        }
                    }
                    cls._instance.file_lock = Lock()
        return cls._instance
    
    async def initialize(self):
        """Создаем базу и загружаем данные"""
        try:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)

            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)

                self.data.update(loaded_data)

                if isinstance(self.data.get("banned_users"), list):
                    self.data["banned_users"] = set(self.data["banned_users"])
                
                logger.info(f"Database loaded from {self.db_file}")
            else:
                await self._save_data()
                logger.info(f"New database created at {self.db_file}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _save_data(self):
        """Сохраняем данные в JSON формате"""
        try:
            with self.file_lock:
                data_to_save = self.data.copy()
                data_to_save["banned_users"] = list(self.data["banned_users"])
                
                with open(self.db_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise
    
    async def add_user(self, user_id: int, username: str = None):
        """Добавляем информацю о пользователе или обновляем"""
        user_key = str(user_id)
        current_time = datetime.now().isoformat()
        
        if user_key not in self.data["users"]:
            self.data["users"][user_key] = {
                "id": user_id,
                "username": username,
                "created_at": current_time,
                "last_active": current_time,
                "task_count": 0,
                "language": "ru"
            }
            logger.info(f"New user added: {user_id} ({username})")
        else:
            self.data["users"][user_key]["last_active"] = current_time
            if username:
                self.data["users"][user_key]["username"] = username
        
        await self._save_data()
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получаем информацию по ID"""
        user_key = str(user_id)
        return self.data["users"].get(user_key)
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получаем всех пользователей"""
        return list(self.data["users"].values())
    
    async def ban_user(self, user_id: int):
        """Блокировка"""
        self.data["banned_users"].add(user_id)
        await self._save_data()
        logger.info(f"User {user_id} has been banned")
    
    async def unban_user(self, user_id: int):
        """Разблокировка"""
        self.data["banned_users"].discard(user_id)
        await self._save_data()
        logger.info(f"User {user_id} has been unbanned")
    
    async def is_user_banned(self, user_id: int) -> bool:
        return user_id in self.data["banned_users"]
    
    async def add_task(self, user_id: int, title: str, description: str = "", priority: str = "medium") -> str:
        """Новая задача у пользователя"""
        task_id = f"{user_id}_{int(datetime.now().timestamp())}"
        current_time = datetime.now().isoformat()

        if "tasks" not in self.data:
            self.data["tasks"] = {}
        
        self.data["tasks"][task_id] = {
            "id": task_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        #Число задач пользователя
        user_key = str(user_id)
        if user_key in self.data["users"]:
            self.data["users"][user_key]["task_count"] += 1
        
        #Статистика
        self.data["statistics"]["total_tasks_created"] += 1
        
        await self._save_data()
        logger.info(f"Task {task_id} added for user {user_id}: {title}")
        
        return task_id
    
    async def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Получаем все задачи по пользователю"""
        if "tasks" not in self.data:
            return []
        
        user_tasks = []
        for task in self.data["tasks"].values():
            if task["user_id"] == user_id:
                user_tasks.append(task)

        user_tasks.sort(key=lambda x: x["created_at"], reverse=True)
        return user_tasks
    
    async def update_task_status(self, task_id: str, completed: bool):
        """Обновляем статус выполнения задачи"""
        if task_id in self.data["tasks"]:
            self.data["tasks"][task_id]["completed"] = completed
            self.data["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            await self._save_data()
            logger.info(f"Task {task_id} status updated to {completed}")
    
    async def delete_task(self, task_id: str):
        """Удаление задачи"""
        if task_id in self.data["tasks"]:
            task = self.data["tasks"][task_id]
            user_id = task["user_id"]
            
            del self.data["tasks"][task_id]
            
            #Обновляем число задач по пользователю
            user_key = str(user_id)
            if user_key in self.data["users"]:
                self.data["users"][user_key]["task_count"] = max(0, 
                    self.data["users"][user_key]["task_count"] - 1)
            
            await self._save_data()
            logger.info(f"Task {task_id} deleted")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Статистика по боту"""
        total_users = len(self.data["users"])
        total_tasks = len(self.data.get("tasks", {}))

        completed_tasks = sum(1 for task in self.data.get("tasks", {}).values() 
                            if task.get("completed", False))

        #Число активных пользователей за последние сутки
        yesterday = datetime.now() - timedelta(days=1)
        active_users = 0
        
        for user in self.data["users"].values():
            try:
                last_active = datetime.fromisoformat(user.get("last_active", ""))
                if last_active > yesterday:
                    active_users += 1
            except:
                continue
        
        return {
            "total_users": total_users,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "active_users_today": active_users,
            "banned_users": len(self.data["banned_users"]),
            **self.data["statistics"]
        }
    
    async def update_statistics(self, stat_name: str, increment: int = 1):
        """Обновляем данные по статистике"""
        if stat_name in self.data["statistics"]:
            self.data["statistics"][stat_name] += increment
        else:
            self.data["statistics"][stat_name] = increment
        await self._save_data()
