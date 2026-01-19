import pinecone

from settings import settings


def initiate_pinecone() -> pinecone.Index:
    pinecone.init(
        api_key=settings.PINECONE_API_KEY,  # find at app.pinecone.io
        environment=settings.PINECONE_ENV_KEY,  # next to api key in console
    )
    index_name = settings.PINECONE_INDEX_NAME
    index = pinecone.Index(index_name)
    return index
