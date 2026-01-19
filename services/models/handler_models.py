import dataclasses
import logging
import datetime
from typing import Optional

logger = logging.getLogger("handler_models")


@dataclasses.dataclass
class FromUser:
    full_name: str


@dataclasses.dataclass
class MockAiogramMessage:
    """
    A message stubbed class imitating aiogram.Message used for integration tests
    """
    text: str  # user message
    from_id: int  # sender user id
    from_user: FromUser  # sender user name
    date: datetime.datetime

    async def answer(self, text: str, parse_mode: Optional[str] = None):
        if len(text) > 4000:
            raise Exception(f"The message is too long: {len(text)}")
        logger.info(f"Answer added char_len=={len(text)}, parse_mode={parse_mode}: {text}")
        return self

    async def delete(self):
        logger.info("Answer deleted")
