from abc import ABC, abstractmethod

from services.memory.redis_handler import RedisConnect


class UpdateValidator(ABC):

    @abstractmethod
    def validate_update(self, update_id: str) -> bool:
        ...


class RedisUpdateValidator(UpdateValidator):

    def validate_update(self, update_id: str) -> bool:
        """
        check if telegram update_id is already processing
        """

        r = RedisConnect().get_connection()

        if r.get(update_id) == 'processing':
            return False

        r.set(update_id, 'processing')
        return True