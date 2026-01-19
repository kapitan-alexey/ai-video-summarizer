import logging

from services.discuss.vectorized_content import VectorizedContentClient
from services.handlers.base_handler import Handler
from services.memory.state_management import DiscussionThreadMetadataClient
from services.models.handler_models import MockAiogramMessage
from services.summary.workflow import SummaryWorkflow
from services.youtube_link_handler import YoutubeLinkHandlerRe
from settings import bot_messages

logger = logging.getLogger("new_link_handler")

MESSAGE_SIZE = 4000

class NewLinkHandler(Handler):
    def __init__(
            self,
            discussion_metadata_client: DiscussionThreadMetadataClient,
            youtube_handler: YoutubeLinkHandlerRe,
            summary_workflow: SummaryWorkflow,
            vectorized_content_client: VectorizedContentClient,
    ):
        self._discussion_metadata_client = discussion_metadata_client
        self._youtube_handler = youtube_handler
        self._summary_workflow = summary_workflow
        self._vectorized_content_client = vectorized_content_client

    async def execute(self, message: MockAiogramMessage):
        video_id = self._youtube_handler.get_video_id(message.text)
        self._discussion_metadata_client.start_new_discussion(
            user_id=message.from_id,
            video_id=video_id
        )
        message_processing = await message.answer(bot_messages.SUMMARIZATION_STARTED)
        content, summary = self._summary_workflow.summarize(video_id)
        await message_processing.delete()
        if len(summary) <= MESSAGE_SIZE:
            await message.answer(summary, parse_mode="markdown")
        else:
            await self._split_answer(message, summary)
        if content:
            self._vectorized_content_client.save(content, video_id)
            await message.answer(bot_messages.POST_SUMMARY_MESSAGE)

    async def _split_answer(self, message: MockAiogramMessage, text: str):
        chunks = text.strip().split("\n")
        merged = ""
        for chunk in chunks:
            if len(merged) + len(chunk) < MESSAGE_SIZE:
                merged += "\n" + chunk
            elif len(merged) + len(chunk) >= MESSAGE_SIZE:
                await message.answer(merged, parse_mode="markdown")
                merged = ""
        if merged:
            await message.answer(merged, parse_mode="markdown")
