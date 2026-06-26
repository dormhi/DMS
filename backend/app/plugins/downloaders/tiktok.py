import re
from .ytdlp_base import YTDLPBaseDownloader

class TikTokDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?(tiktok\.com|vt\.tiktok\.com)', url))
