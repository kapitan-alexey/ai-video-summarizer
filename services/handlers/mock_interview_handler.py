import logging

from aiogram.types import Message
from langchain.chains import ConversationChain

from services.handlers.base_handler import Handler

logger = logging.getLogger("mock_interview_handler")


class MockInterviewHandler(Handler):
    def __init__(self, chat_chain: ConversationChain):
        self._chat_chain = chat_chain

    async def execute(self, message: Message):
        response = (
            self._chat_chain("Could you take a Systems Design Mock interview for me, please?")
            if message.text.startswith("/mockme")
            else self._chat_chain(message.text)
        )
        await message.answer(response["response"])
