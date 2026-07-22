import re
from .ytdlp_base import YTDLPBaseDownloader

class KickDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?kick\.com', url))

    def get_ydl_opts(self, output_dir: str) -> dict:
        opts = super().get_ydl_opts(output_dir)
        opts.update({
            'concurrent_fragment_downloads': 8,
            'retries': 30,
            'fragment_retries': 30,
            'extractor_retries': 5,
            'throttledratelimit': None,
            'live_from_start': True,
            'hls_use_mpegts': True,
            'socket_timeout': 120,
            'wait_for_video': (60, 180),
        })
        return opts
