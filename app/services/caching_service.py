import json
from typing import Optional, Callable, Any
from core.redis_client import redis_client

import logging

logger = logging.getLogger("cache")


class CachingService:
    def get_from_cache(self, key: str) -> Optional[Any]:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def set_to_cache(self, key: str, value: Any, ttl: int = 60) -> None:
        # Если объект является экземпляром SQLAlchemy, преобразуем в словарь
        if hasattr(value, "as_dict"):
            value = value.as_dict()
        # Если список содержит объекты SQLAlchemy, преобразуем каждый в словарь
        elif isinstance(value, list) and len(value) > 0 and hasattr(value[0], "as_dict"):
            value = [item.as_dict() for item in value]
        redis_client.set(key, json.dumps(value), ex=ttl)

    def invalidate_cache(self, key: str) -> None:
        redis_client.delete(key)

    def cache_result(self, key: str, ttl: int = 60) -> Callable:
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                cached_data = self.get_from_cache(key)
                logger.info(f"ЗАКЭШИРОВАНО - {cached_data}")
                if cached_data is not None:
                    return cached_data
                result = func(*args, **kwargs)
                self.set_to_cache(key, result, ttl)
                return result

            return wrapper

        return decorator
