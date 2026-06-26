from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.job import Job, JobState
import time

@celery_app.task(bind=True)
def process_media_job(self, job_id: int):
    # This is just a stub for Day 2. Actual processing logic comes in Days 3-4
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        db.close()
        return "Job not found"
    
    try:
        # State transitions simulation
        job.state = JobState.DOWNLOADING
        db.commit()
        time.sleep(2) # Simulate download
        
        job.state = JobState.PROCESSING
        db.commit()
        time.sleep(2) # Simulate processing
        
        job.state = JobState.COMPLETED
        db.commit()
        
    except Exception as e:
        job.state = JobState.FAILED
        job.error_message = str(e)
        db.commit()
        
    finally:
        db.close()
        
    return "Job finished"
