from abc import ABC, abstractmethod
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List


class SubtitleSplitter(ABC):

    @abstractmethod
    def split_subtitles(self, subtitles: str) -> List[Document]:
        ...


class SubtitleRecursiveSplitter(SubtitleSplitter):

    def split_subtitles(self, subtitles: str) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=1000,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_text(subtitles)
