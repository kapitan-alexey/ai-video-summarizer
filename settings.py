import logging

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    PINECONE_API_KEY: str
    PINECONE_ENV_KEY: str

    PINECONE_INDEX_NAME: str


class BotMessages(BaseSettings):
    POST_SUMMARY_MESSAGE: str = 'Would you like to discuss this video?'
    SUMMARIZATION_STARTED: str = 'Give me a sec! I am summarizing your video now. Please wait ...'
    INCORRECT_YOUTUBE_LINK: str = '"{}" is not a youtube link. Please use valid youtube link.'
    CANNOT_ANSWER: str = "Sorry, there is no such info in the video"
    START_MOCK_INTERVIEW: str = (
        "I am happy to be your System Design Interview companion."
        "Do you have any preferences about the topics that you want to be interviewed for?"
    )


settings = Settings()
bot_messages = BotMessages()
