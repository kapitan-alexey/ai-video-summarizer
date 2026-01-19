from abc import ABC, abstractmethod

from functional import seq
from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

from settings import settings

SUMMARY_LESSON = "\n**Summarised study material:**"


class Summarizer(ABC):

    @abstractmethod
    def summarize(self, content: str) -> str:
        ...

    @property
    @abstractmethod
    def type(self) -> str:
        ...


class ConciseSplitSummarizer(Summarizer):
    """
    Splits the content in chunks to obtain summaries.
    All summaries are then concatenated to obtain final summary
    """

    @property
    def type(self) -> str:
        return "concise"

    def __init__(self, llm: ChatOpenAI):
        self._llm = llm
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000, chunk_overlap=50, separators=[" ", ",", "\n"]
        )
        map_prompt_template = """
                              Write a summary of this chunk of text from video that includes the main points and any important details.
                              {text}
                              """
        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
        combine_prompt_template = """
                                    You will get subtitles from a video as a text.
                                    Write a concise summary of the following text from video delimited by triple backquotes.
                                    Return your response in this format (delimited by backquotes):
                                    short summary should be about 10 words length and should describe what is this video all about.
                                    'Short summary of video:
                                    Key points of the video:'
                                    ```{text}```
                                    SHORT GENERAL SUMMARY:
                                    BULLET POINT SUMMARY:
                                    """
        combine_prompt = PromptTemplate(
            template=combine_prompt_template, input_variables=["text"]
        )
        self._chain = load_summarize_chain(
            self._llm,
            chain_type='map_reduce',
            verbose=False,
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            return_intermediate_steps=True,
        )

    def summarize(self, subtitles):
        docs = [Document(page_content=t) for t in self._splitter.split_text(subtitles)]
        result = self._chain({"input_documents": docs})
        return result['output_text']


class DetailedSplitSummarizer(Summarizer):
    """
    Splits the content in chunks to obtain summaries.
    All summaries are then concatenated to obtain final summary
    """

    @property
    def type(self) -> str:
        return "detailed"

    def __init__(self, llm: ChatOpenAI):
        self._llm = llm
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000, chunk_overlap=100, separators=[" ", ",", "\n"]
        )
        self._summary_chain = StuffDocumentsChain(
            llm_chain=LLMChain(
                llm=self._llm,
                prompt=PromptTemplate(
                    template=""""Please, summarize the following into several sentences."
                            "In your answer you are allowed to use regular paragraphs as well as bullet points"
                            "if those could help the reader grasp the content" \n ```{text}```""",
                    input_variables=["text"]
                ),
                verbose=True,
            ),
        )
        self._chain = load_summarize_chain(
            llm=self._llm,
            verbose=True,
            prompt=PromptTemplate(
                template=(
                    "You are a Software Systems Design Tutor. You are helping your students to study"
                    "written content. You are asked to use the following text as an input and produce"
                    "a comprehensive and organized written content, so that a student would use it to "
                    "learn familiarize with the content in details. Make the text logical and avoid repetitions. "
                    "You also know that your students love sub-titles, bullet points, and summarizing passages"
                    "\n ```{text}```"

                ),
                input_variables=["text"]
            )
        )

        self._brief_summarizer = ConciseSplitSummarizer(llm)

    def summarize(self, subtitles: str):
        chunks = self._splitter.split_text(subtitles)
        concatenated = (
            seq(chunks)
            .map(lambda chunk: Document(page_content=chunk))
            .map(lambda doc: self._summary_chain([doc]))
            .map(lambda s: s["output_text"])
            .make_string("\n\n")
        )
        short = self._brief_summarizer.summarize(concatenated)
        detailed = self._chain([Document(page_content=concatenated)])['output_text']

        return f"**Brief Summary:** {short}\n\n{SUMMARY_LESSON}\n{detailed}"


if __name__ == '__main__':
    text = """
    Whenever possible, PyFunctional will compute lazily. This is accomplished by tracking the list of transformations that have been applied to the sequence and only evaluating them when an action is called. In PyFunctional this is called tracking lineage. This is also responsible for the ability for PyFunctional to cache results of computation to prevent expensive re-computation. This is predominantly done to preserve sensible behavior and used sparingly. For example, calling size() will cache the underlying sequence. If this was not done and the input was an iterator, then further calls would operate on an expired iterator since it was used to compute the length. Similarly, repr also caches since it is most often used during interactive sessions where its undesirable to keep recomputing the same value. Below are some examples of inspecting lineage.
    """
    llm = ChatOpenAI()
    detailed = DetailedSplitSummarizer(llm)
    detailed.summarize(text)
