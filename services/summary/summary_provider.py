from abc import ABC, abstractmethod

from youtube_transcript_api import YouTubeTranscriptApi
from typing import Any


class YoutubeSubtitleReceiver(ABC):
    
    @abstractmethod
    def get_youtube_subtitles(self, video_id: str):
        ...

    @abstractmethod
    def list_subtitles(self, video_id: str):
        ...


class SubtitlesProvider(YoutubeSubtitleReceiver):

    def get_youtube_subtitles(self, video_id: str) -> Any:
        """
        get subtitles of youtube video
        """
        return YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en', 'en-GB', 'ru', 'de'])
    
    def list_subtitles(self, video_id: str):
        return YouTubeTranscriptApi.list_transcripts(video_id)
