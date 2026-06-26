from abc import ABC, abstractmethod
from typing import Optional

class BaseDownloader(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Returns True if this downloader can handle the given URL."""
        pass
        
    @abstractmethod
    def download(self, url: str, output_dir: str) -> Optional[str]:
        """Downloads the media and returns the path to the downloaded file."""
        pass

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, file_path: str) -> str:
        """Processes (analyzes, repairs, optimizes) the media and returns the new path."""
        pass
