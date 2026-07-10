import os
import yt_dlp
from typing import Optional
from app.plugins.base import BaseDownloader

class YTDLPBaseDownloader(BaseDownloader):
    def get_ydl_opts(self, output_dir: str) -> dict:
        return {
            'outtmpl': os.path.join(output_dir, '%(title).80s_%(id)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': True,
            # Retry and timeout settings for long downloads
            'retries': 10,
            'fragment_retries': 10,
            'file_access_retries': 5,
            'socket_timeout': 30,
            # Continue partial downloads
            'continuedl': True,
            # Don't abort on unavailable fragments (common in long VODs)
            'skip_unavailable_fragments': True,
            # Buffer size for faster downloads
            'buffersize': 1024 * 1024,  # 1MB buffer
        }

    def download(self, url: str, output_dir: str) -> Optional[str]:
        os.makedirs(output_dir, exist_ok=True)
        opts = self.get_ydl_opts(output_dir)
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    return None
                
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                
                # Check for merged output or fallback to original
                for ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(f"{base}{ext}"):
                        return f"{base}{ext}"
                        
                if os.path.exists(filename):
                    return filename
                    
                raise Exception("Downloaded file not found on disk.")
        except Exception as e:
            import logging
            logging.error(f"Error downloading {url}: {e}")
            raise
