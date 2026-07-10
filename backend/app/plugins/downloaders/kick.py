import re
from .ytdlp_base import YTDLPBaseDownloader

class KickDownloader(YTDLPBaseDownloader):
    def can_handle(self, url: str) -> bool:
        return bool(re.search(r'(?:https?://)?(?:www\.)?kick\.com', url))

    def get_ydl_opts(self, output_dir: str) -> dict:
        opts = super().get_ydl_opts(output_dir)
        # Kick-specific: VODs are HLS streams, need concurrent fragment downloads
        opts.update({
            'concurrent_fragment_downloads': 5,
            # Kick VODs can be very long, increase retries
            'retries': 20,
            'fragment_retries': 20,
            # Some Kick VODs need cookies or specific extractor args
            'extractor_args': {'kick': {'api_host': 'kick.com'}},
            # Don't limit download speed
            'throttledratelimit': None,
        })
        return opts
