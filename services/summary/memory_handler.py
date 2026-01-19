import logging
from abc import ABC, abstractmethod

from services.memory.redis_handler import RedisConnect

logger = logging.getLogger("memory_handler")


class MemoryHandler(ABC):

    @abstractmethod
    def get_data(self, key: str):
        ...

    @abstractmethod
    def save_data(self, key: str, value):
        ...


class MemoryHandlerRedis(MemoryHandler):

    def __init__(self) -> None:
        self.r = RedisConnect().get_connection()

    def get_data(self, key: str):
        res = self.r.get(key)
        logger.info(f"Took data from redis for the key: {key}")
        return res

    def delete(self, key: str):
        res = self.r.delete(key)
        logger.info(f"Deleted data from redis for the key: {key}")
        return res

    def save_data(self, key: str, value):
        self.r.set(key, value)
        logger.info(f'Saved data to redis for the key: {key}')
