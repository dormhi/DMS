import subprocess
import json
import logging

def analyze_media(file_path: str) -> dict:
    """Returns video and audio codec info using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=codec_type,codec_name",
        "-of", "json",
        file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)
        
        info = {"video_codec": None, "audio_codec": None}
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                info["video_codec"] = stream.get("codec_name")
            elif stream.get("codec_type") == "audio":
                info["audio_codec"] = stream.get("codec_name")
        return info
    except Exception as e:
        logging.error(f"FFprobe failed for {file_path}: {e}")
        return {}
