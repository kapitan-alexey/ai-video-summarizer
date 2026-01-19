import logging

from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain

from services.handlers.base_handler import Handler
from services.models.handler_models import MockAiogramMessage
from settings import bot_messages

logger = logging.getLogger("conversation_handler")


class ConversationHandler(Handler):
    def __init__(self, _chat_chain: BaseConversationalRetrievalChain):
        self._chat_chain = _chat_chain

    async def execute(self, message: MockAiogramMessage):
        response = self._chat_chain(message.text)
        logger.info(f'Response: {response}')
        await message.answer(response["answer"])
