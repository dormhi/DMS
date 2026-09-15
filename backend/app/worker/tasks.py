from app.worker.celery_app import celery_app
from app.db.session import SessionLocal, init_db
from app.db.models.job import Job, JobState
from app.plugins.downloaders.factory import get_downloader
from app.services.archive_cleanup import cleanup_archive
from app.telegram.status import JobStatusNotifier, safe_error_summary
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

    notifier = JobStatusNotifier(job)
    try:
        # If file already exists (e.g. Telegram upload), skip download
        if job.file_path and os.path.exists(job.file_path):
            logging.info(f"Skipping download, file already exists: {job.file_path}")
        else:
            # 1. Download Phase
            job.state = JobState.DOWNLOADING
            db.commit()
            notifier.update(f"📥 İş #{job.id} indiriliyor...")

            downloader = get_downloader(job.original_url)
            downloaded_file = downloader.download(
                job.original_url,
                DOWNLOAD_DIR,
                progress_callback=notifier.download_progress,
            )

            if not downloaded_file:
                raise Exception("Download failed, no file returned.")

            job.file_path = downloaded_file

        job.state = JobState.PROCESSING
        db.commit()
        notifier.update(f"⚙️ İş #{job.id} işleniyor / uyumluluk kontrolü yapılıyor...")

        # 2. Processing Phase
        downloaded_file = job.file_path
        from app.plugins.processors.normalize import NormalizeProcessor
        processor = NormalizeProcessor()
        final_file_path = processor.process(downloaded_file)
        
        job.file_path = final_file_path
        
        # 3. Uploading Phase (Telegram only for files under 50MB)
        delivery_error = None
        if job.chat_id:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            file_size = os.path.getsize(final_file_path) if os.path.exists(final_file_path) else 0
            max_telegram_size = 50 * 1024 * 1024  # 50MB

            if bot_token and file_size > 0 and file_size <= max_telegram_size:
                job.state = JobState.UPLOADING
                db.commit()
                notifier.update(f"📤 İş #{job.id} Telegram'a gönderiliyor...")

                tg_url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
                try:
                    with open(final_file_path, "rb") as video_file:
                        resp = requests.post(
                            tg_url,
                            data={"chat_id": job.chat_id, "caption": "✅ İşleminiz başarıyla tamamlandı!"},
                            files={"video": video_file},
                            timeout=300,
                        )
                    if not resp.ok:
                        delivery_error = safe_error_summary(resp.text)
                        logging.error("Telegram upload failed: %s", delivery_error)
                except (OSError, requests.RequestException) as e:
                    delivery_error = safe_error_summary(e)
                    logging.exception("Telegram upload request failed")
            elif bot_token and file_size > max_telegram_size:
                size_mb = round(file_size / (1024 * 1024))
                delivery_error = f"Dosya {size_mb} MB ve Telegram gönderim limitinin üzerinde."
            elif not bot_token:
                delivery_error = "Telegram bot yapılandırması eksik."
                        
        job.state = JobState.COMPLETED
        db.commit()
        if delivery_error:
            notifier.update(
                f"✅ İş #{job.id} tamamlandı, ancak Telegram'a gönderilemedi.\n"
                f"Neden: {delivery_error}\n📥 Dosya web kütüphanesinde hazır."
            )
        else:
            notifier.update(f"✅ İş #{job.id} başarıyla tamamlandı.")
        # Enforce the storage quota immediately after new media is available.
        cleanup_archive_task.delay()
        
    except Exception as e:
        job.state = JobState.FAILED
        job.error_message = safe_error_summary(e)
        db.commit()
        notifier.update(f"❌ İş #{job.id} başarısız.\nNeden: {job.error_message}")
        
    finally:
        db.close()
        
    return "Job finished"


@celery_app.task(name="app.worker.tasks.cleanup_archive_task")
def cleanup_archive_task():
    """Scheduled archive retention and quota enforcement."""
    db = SessionLocal()
    try:
        return cleanup_archive(db, DOWNLOAD_DIR)
    finally:
        db.close()
