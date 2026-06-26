import re
from .ytdlp_base import YTDLPBaseDownloader

class TwitchDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?twitch\.tv', url))
