import pinecone
import uuid
from typing import List

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

from settings import settings
from services.discuss.subtitles_splitter import SubtitleRecursiveSplitter


class VectorizedContentClient:
    """Manages vectorized content"""

    def __init__(
            self,
            pinecone_index: pinecone.Index,
            splitter: SubtitleRecursiveSplitter,
            vector_embedder: OpenAIEmbeddings,
    ):
        self._pinecone_index = pinecone_index
        self._splitter = splitter
        self._vector_embedder = vector_embedder
        self._docsearch = Pinecone.from_existing_index(
            settings.PINECONE_INDEX_NAME,
            self._vector_embedder
        )

    def save(self, content: str, video_id: str) -> None:
        """Converts the content into pinecone documents and stores them"""
        if video_id in self._pinecone_index.describe_index_stats()['namespaces']:
            print(f'Video {video_id} is already in pinecone.')
            return None
        vector_store = Pinecone(
            index=self._pinecone_index,
            embedding=self._vector_embedder,
            text_key="text",
            namespace=video_id,
        )
        vector_store.add_texts(
            texts=self._splitter.split_subtitles(content),
            namespace=video_id
        )
        print(f'Video {video_id} is uploaded to pinecone')

    def retrieve(self, namespace: str, text: str):
        return self._docsearch.similarity_search(text, k=2, namespace=namespace)
