import os
import subprocess
import logging
from app.plugins.base import BaseProcessor
from .ffprobe import analyze_media

class NormalizeProcessor(BaseProcessor):
    def process(self, file_path: str) -> str:
        """
        Analyzes the file. If it's already mp4 with h264/aac, returns it.
        Otherwise, intelligently normalizes it with ffmpeg.
        Returns the path to the normalized file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        info = analyze_media(file_path)
        video_codec = info.get("video_codec")
        audio_codec = info.get("audio_codec")
        
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_normalized.mp4"
        
        needs_video_transcode = video_codec != "h264"
        needs_audio_transcode = audio_codec != "aac"
        
        if not needs_video_transcode and not needs_audio_transcode and ext == ".mp4":
            logging.info(f"File {file_path} is already optimized.")
            return file_path
            
        cmd = ["ffmpeg", "-y", "-i", file_path]
        
        if needs_video_transcode:
            cmd.extend(["-c:v", "libx264", "-crf", "23", "-preset", "fast"])
        else:
            cmd.extend(["-c:v", "copy"])
            
        if needs_audio_transcode:
            cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        else:
            cmd.extend(["-c:a", "copy"])
            
        cmd.append(output_path)
        
        try:
            logging.info(f"Running FFmpeg: {' '.join(cmd)}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # Optionally delete original file to save space
            if os.path.exists(output_path):
                os.remove(file_path)
                return output_path
            else:
                raise Exception("FFmpeg output not found.")
        except Exception as e:
            logging.error(f"Normalization failed: {e}")
            raise
