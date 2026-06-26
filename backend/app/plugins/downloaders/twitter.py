import re
from .ytdlp_base import YTDLPBaseDownloader

class TwitterDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?(twitter\.com|x\.com)', url))
