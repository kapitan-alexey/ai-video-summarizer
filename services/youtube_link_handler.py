from abc import ABC, abstractmethod

import re


class YoutubeLinkHandler(ABC):

    @abstractmethod
    def is_youtube_link(self, input_string: str) -> bool:
        ...
    
    @abstractmethod
    def get_video_id(self, link: str) -> str:
        ...


class YoutubeLinkHandlerRe(YoutubeLinkHandler):

    def is_youtube_link(self, input_string: str) -> bool:
        # Regular expression pattern to match YouTube video URLs
        youtube_pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/user/[^/]+/u/[^/]+/|youtube\.com/attribution_link\?a=|youtube\.com/[^/]+/[^/]+/|youtu\.be/|youtube\.com[^"\s]*)([a-zA-Z0-9_-]{11})'

        # Use re.match to check if the input_string matches the pattern
        if re.match(youtube_pattern, input_string):
            return True
        return False

    def get_video_id(self, link: str) -> str:
        # Define a regular expression pattern to match YouTube video URIs
        youtube_uri_pattern = r'(https?://)?(www\.)?(youtu\.be/|youtube\.com/watch\?v=|youtube\.com/embed/)([\w-]+)'
    
        # Use the re.search function to find a match
        match = re.search(youtube_uri_pattern, link)
    
        if match:
            # Extract the video_id
            video_id = match.group(4)
            return video_id
        else:
            raise ValueError("The provided URI is not a valid YouTube URI or does not contain a video_id.")
