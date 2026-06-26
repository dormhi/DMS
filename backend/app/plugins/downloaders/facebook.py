import re
from .ytdlp_base import YTDLPBaseDownloader

class FacebookDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?facebook\.com|fb\.watch', url))
