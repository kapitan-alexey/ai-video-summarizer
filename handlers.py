import asyncio
import logging
import datetime
from typing import Union

from aiogram import types
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from services.handlers.handler_factories import create_handler, create_interview_mock_starter_handler
from services.models.handler_models import MockAiogramMessage, FromUser
from services.summary.memory_handler import MemoryHandlerRedis

logger = logging.getLogger('handlers')


async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(
        f"Hello, {message.from_user.full_name}!, I a bot helping to summarize and discuss Youtube videos. "
        f"Just share any Youtube Video link with me and I will summarize it for you. "
    )


async def echo_handler(message: types.Message, state: FSMContext) -> None:
    """
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    await handle_chat_message(message)


async def handle_chat_message(message: Union[MockAiogramMessage, types.Message]):
    handler = await create_handler(message)
    await handler.execute(message)


async def mock_interview_start_handler(message: Union[MockAiogramMessage, types.Message]):
    handler = await create_interview_mock_starter_handler(message)
    await handler.execute(message)


if __name__ == '__main__':
    link = "https://www.youtube.com/watch?v=bBTPZ9NdSk8"
    link_id = link.split("=")[1]
    res = MemoryHandlerRedis().delete(f"detailed:{link_id}")
    asyncio.get_event_loop().run_until_complete(
        handle_chat_message(
            MockAiogramMessage(
                text=link,
                from_id=123,
                from_user=FromUser(
                    full_name="YB"
                ),
                date=datetime.datetime(year=2023, month=11, day=7, second=2)
            )
        )
    )
