from typing import Optional
from app.plugins.base import BaseDownloader
from .kick import KickDownloader
from .youtube import YouTubeDownloader
from .facebook import FacebookDownloader
from .twitter import TwitterDownloader
from .twitch import TwitchDownloader
from .tiktok import TikTokDownloader
from .ytdlp_base import YTDLPBaseDownloader

class GenericDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return True

def get_downloader(url: str) -> BaseDownloader:
    downloaders = [
        KickDownloader(),
        YouTubeDownloader(),
        FacebookDownloader(),
        TwitterDownloader(),
        TwitchDownloader(),
        TikTokDownloader()
    ]
    
    for downloader in downloaders:
        if downloader.can_handle(url):
            return downloader
            
    return GenericDownloader()
