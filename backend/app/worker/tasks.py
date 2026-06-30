from app.worker.celery_app import celery_app
from app.db.session import SessionLocal, init_db
from app.db.models.job import Job, JobState
from app.plugins.downloaders.factory import get_downloader
import time
import os
import requests
import logging

# Create tables if they don't exist yet (worker runs as separate process)
init_db()

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/data/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@celery_app.task(bind=True)
def process_media_job(self, job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        db.close()
        return "Job not found"
    
    try:
        # 1. Download Phase
        job.state = JobState.DOWNLOADING
        db.commit()
        
        downloader = get_downloader(job.original_url)
        downloaded_file = downloader.download(job.original_url, DOWNLOAD_DIR)
        
        if not downloaded_file:
            raise Exception("Download failed, no file returned.")
            
        job.file_path = downloaded_file
        job.state = JobState.PROCESSING
        db.commit()
        
        # 2. Processing Phase
        from app.plugins.processors.normalize import NormalizeProcessor
        processor = NormalizeProcessor()
        final_file_path = processor.process(downloaded_file)
        
        job.file_path = final_file_path
        
        # 3. Uploading Phase
        if job.chat_id:
            job.state = JobState.UPLOADING
            db.commit()
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if bot_token and os.path.exists(final_file_path):
                url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
                with open(final_file_path, "rb") as video_file:
                    resp = requests.post(
                        url,
                        data={"chat_id": job.chat_id, "caption": "✅ İşleminiz başarıyla tamamlandı!"},
                        files={"video": video_file}
                    )
                    if resp.status_code != 200:
                        logging.error(f"Telegram upload failed: {resp.text}")
                        
        job.state = JobState.COMPLETED
        db.commit()
        
    except Exception as e:
        job.state = JobState.FAILED
        job.error_message = str(e)
        db.commit()
        
    finally:
        db.close()
        
    return "Job finished"
