from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.job import Job, JobState
from app.plugins.downloaders.factory import get_downloader
import time
import os

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/data/downloads")

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
        
        # 2. Processing Phase (To be implemented in Day 4)
        time.sleep(1) # Stub for Day 4 processing logic
        
        job.state = JobState.COMPLETED
        db.commit()
        
    except Exception as e:
        job.state = JobState.FAILED
        job.error_message = str(e)
        db.commit()
        
    finally:
        db.close()
        
    return "Job finished"
