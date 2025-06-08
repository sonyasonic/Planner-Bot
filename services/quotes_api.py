"""
Интеграция с ZenQuotes API для получения цитат для мотивации пользователя
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any
import aiohttp

from config import Config

logger = logging.getLogger(__name__)


class QuotesAPI:
    """Взаимодействие с сервисом ZenQuotes API"""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.ZENQUOTES_API_URL
        self.cache = {}
        self.cache_duration = self.config.CACHE_DURATION
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def get_random_quote(self) -> Optional[Dict[str, Any]]:
        """
        Получает цитату с указанного сайта, кэширует и возвращает пользователю, если сработало
        """
        cache_key = "random_quote"
        current_time = time.time()

        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if current_time - cached_time < self.cache_duration:
                logger.info("Returning cached quote")
                return cached_data
        
        try:
            #API запрос
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info(f"Делаю запрос с ZenQuotes API: {self.base_url}")
                
                async with session.get(self.base_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # ZenQuotes возвращает список, поэтому обрабатываем
                        if isinstance(data, list) and len(data) > 0:
                            quote_data = data[0]
                            
                            #Разделяем автора цитаты и ее текст
                            quote_text = quote_data.get('q', '').strip()
                            author = quote_data.get('a', 'Unknown').strip()
                            
                            if quote_text:
                                formatted_quote = {
                                    'text': quote_text,
                                    'author': author
                                }
                                
                                #Кэшируем
                                self.cache[cache_key] = (formatted_quote, current_time)
                                
                                logger.info(f"Успешно получена цитата от {author}")
                                return formatted_quote
                            else:
                                logger.warning("Текст цитаты отсутствует")
                                return None
                        else:
                            logger.warning("API вернул неправильный формат даты или данные отсутствуют")
                            return None
                    else:
                        logger.error(f"API запрос не удался, код {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("Вышло время с запроса от ZenQuotes API")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching quote: {e}")
            return None
    
    def clear_cache(self):
        """Очищаем кэш"""
        self.cache.clear()
        logger.info("Кэш очищен")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Информация о статусе кэширования"""
        current_time = time.time()
        cache_info = {}
        
        for key, (data, cached_time) in self.cache.items():
            age = current_time - cached_time
            is_expired = age >= self.cache_duration
            cache_info[key] = {
                'age_seconds': int(age),
                'is_expired': is_expired,
                'data_preview': str(data)[:100] + '...' if len(str(data)) > 100 else str(data)
            }
        
        return cache_info
