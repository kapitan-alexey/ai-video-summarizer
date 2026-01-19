import logging
from abc import ABC, abstractmethod

from services.memory.redis_handler import RedisConnect

logger = logging.getLogger("state_management")

MOCK_INTERVIEW = "MOCK_INTERVIEW"


class BaseDiscussionMetadataClient(ABC):

    @abstractmethod
    def get(self, user_id: str) -> str:
        ...

    @abstractmethod
    def start_new_discussion(self, user_id, video_id: str):
        ...


class DiscussionThreadMetadataClient(BaseDiscussionMetadataClient):
    """ State client that is used to check what exactly the discussion metadata"""

    def __init__(self) -> None:
        self.r = RedisConnect().get_connection()

    def get(self, user_id: int) -> str:
        """Returns video_id for a given user_id used in a discussion thread"""
        return self.r.get(user_id)

    def start_new_discussion(self, user_id: int, video_id: str):
        """
        Configures a discussion thread for a certain user.

        :param user_id: user's id to set the new discussion thread for
        :param video_id: video_id used to initiate the new discussion
        """
        self.r.set(user_id, video_id)
        logger.info(f'User {user_id} starts a new thread for {video_id}')

    def start_mock_interview(self, user_id: int, key: str):
        """
        Configures a discussion thread for a certain user.

        Updates the current state for the user to 'MOCK_INTERVIEW'
        :param user_id: user's id to set the new discussion thread for
        """
        self.r.set(user_id, f"{MOCK_INTERVIEW}:{key}")

    def is_mock_interview_thread(self, user_id: int):
        return self.get(user_id).startswith(MOCK_INTERVIEW)
