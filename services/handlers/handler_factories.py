import logging
from typing import Union

from aiogram.types import Message
from langchain.chains import ConversationalRetrievalChain, ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Pinecone

from services.discuss.pinecone_utils import initiate_pinecone
from services.discuss.subtitles_splitter import SubtitleRecursiveSplitter
from services.discuss.vectorized_content import VectorizedContentClient
from services.handlers.base_handler import Handler
from services.handlers.conversation_chain_prompt import create_prompt
from services.handlers.conversation_handler import ConversationHandler
from services.handlers.mock_interview_handler import MockInterviewHandler
from services.handlers.mock_interview_prompt import MOCK_INTERVIEW_PROMPT
from services.handlers.new_link_handler import NewLinkHandler
from services.memory.redis_handler import CustomRedisChatMessageHistory, RedisConnect
from services.memory.state_management import DiscussionThreadMetadataClient, MOCK_INTERVIEW
from services.models.handler_models import MockAiogramMessage
from services.summary.memory_handler import MemoryHandlerRedis
from services.summary.summarizer import ConciseSplitSummarizer, DetailedSplitSummarizer
from services.summary.summary_provider import SubtitlesProvider
from services.summary.workflow import SummaryWorkflow
from services.youtube_link_handler import YoutubeLinkHandlerRe
from settings import bot_messages, settings

logger = logging.getLogger("handler_factories")

SECOND = 1
MINUTES = 60 * SECOND
HOURS = 60 * MINUTES
DAYS = 24 * HOURS


async def create_handler(message: MockAiogramMessage) -> Handler:
    youtube_handler = YoutubeLinkHandlerRe()
    discussion_metadata_client = DiscussionThreadMetadataClient()
    llm = await _create_llm()

    summary_workflow = SummaryWorkflow(
        memory=MemoryHandlerRedis(),
        summarizer=DetailedSplitSummarizer(llm=llm),
        subtitle_provider=SubtitlesProvider(),
    )

    if youtube_handler.is_youtube_link(message.text):
        vectorized_content_client = VectorizedContentClient(
            pinecone_index=initiate_pinecone(),
            splitter=SubtitleRecursiveSplitter(),
            vector_embedder=OpenAIEmbeddings()
        )
        return NewLinkHandler(
            discussion_metadata_client=discussion_metadata_client,
            youtube_handler=youtube_handler,
            summary_workflow=summary_workflow,
            vectorized_content_client=vectorized_content_client,
        )
    elif discussion_metadata_client.is_mock_interview_thread(message.from_id):
        return await create_interview_mock_handler(message, llm, discussion_metadata_client)

    discussed_video = discussion_metadata_client.get(user_id=message.from_id)
    if not discussed_video:
        await message.answer(bot_messages.INCORRECT_YOUTUBE_LINK.format(message.text))
    history = CustomRedisChatMessageHistory(
        session_id=discussed_video,
        key_prefix=f"message_store:{message.from_id}:",
        connect=RedisConnect(decode_responses=False),
        ttl=2 * DAYS,
    )
    return ConversationHandler(
        _chat_chain=ConversationalRetrievalChain.from_llm(
            llm=llm,
            memory=ConversationBufferMemory(
                memory_key='chat_history',
                return_messages=True,
                output_key='answer',
                chat_memory=history
            ),
            retriever=Pinecone(
                index=initiate_pinecone(),
                embedding=OpenAIEmbeddings(),
                text_key="text",
                namespace=discussed_video,
            ).as_retriever(),
            combine_docs_chain_kwargs={
                "prompt": create_prompt(
                    summary_workflow.summarize(discussed_video)[1]
                )
            },
            verbose=False,
        )
    )


async def create_interview_mock_starter_handler(
        message: Union[Message, MockAiogramMessage],
) -> Handler:
    llm = await _create_llm()
    discussion_metadata_client = DiscussionThreadMetadataClient()
    discussion_metadata_client.start_mock_interview(message.from_id, str(message.date.time()))
    return await create_interview_mock_handler(message, llm, discussion_metadata_client)


async def create_interview_mock_handler(
        message: Union[Message, MockAiogramMessage],
        llm: ChatOpenAI,
        discussion_metadata_client: DiscussionThreadMetadataClient
) -> Handler:
    history = CustomRedisChatMessageHistory(
        session_id=discussion_metadata_client.get(message.from_id),
        key_prefix=f"message_store:{message.from_id}:",
        connect=RedisConnect(decode_responses=False),
        ttl=2 * DAYS,
    )
    chat_chain = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(
            chat_memory=history,
        ),
        prompt=MOCK_INTERVIEW_PROMPT,
        verbose=True,
    )
    return MockInterviewHandler(
        chat_chain=chat_chain
    )


async def _create_llm():
    return ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )
