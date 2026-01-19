from typing import Tuple, Optional

from services.summary.memory_handler import MemoryHandlerRedis
from services.summary.summarizer import ConciseSplitSummarizer, Summarizer
from services.summary.summary_provider import SubtitlesProvider


class SummaryWorkflow:
    def __init__(
            self,
            memory: MemoryHandlerRedis,
            summarizer: Summarizer,
            subtitle_provider: SubtitlesProvider,
    ):
        self._memory = memory
        self._summarizer = summarizer
        self._subtitle_provider = subtitle_provider

    def summarize(self, video_id: str) -> Tuple[Optional[str], str]:
        saved_summary = self._memory.get_data(f"{self._summarizer.type}:{video_id}")
        if saved_summary:
            return None, saved_summary
        subtitles = self._fetch_subtitles(video_id)
        summary = self._summarizer.summarize(subtitles)
        self._memory.save_data(key=f"{self._summarizer.type}:{video_id}", value=summary)
        return subtitles, summary

    def _fetch_subtitles(self, video_id):
        """Uses external API to get subtitles for a video"""
        subtitles_info = self._subtitle_provider.get_youtube_subtitles(video_id)
        subtitles = ' '.join([s['text'] for s in subtitles_info])
        return subtitles
