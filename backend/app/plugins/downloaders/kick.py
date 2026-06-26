import re
from .ytdlp_base import YTDLPBaseDownloader

class KickDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?kick\.com', url))
