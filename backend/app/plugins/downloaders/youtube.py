import re
from .ytdlp_base import YTDLPBaseDownloader

class YouTubeDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?(youtube\.com|youtu\.be)', url))
