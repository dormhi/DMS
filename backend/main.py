import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db, init_db
from app.db.models.job import Job, JobState

# Create DB tables on startup
init_db()

# Ensure downloads directory exists
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/data/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Dormhi Media Server (DMS)",
    description="Centralized media downloading, repairing, and optimization API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve downloaded/processed files as static
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "DMS Backend is running."}

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    # Refresh the session to see latest data from other processes (bot, worker)
    db.expire_all()
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [
        {
            "id": j.id,
            "original_url": j.original_url,
            "file_path": j.file_path,
            "chat_id": j.chat_id,
            "state": j.state.value if j.state else "unknown",
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "updated_at": j.updated_at.isoformat() if j.updated_at else None,
        }
        for j in jobs
    ]

@app.get("/api/jobs/completed")
def get_completed_jobs(db: Session = Depends(get_db)):
    """Return completed jobs that have a file_path (for Library page)."""
    db.expire_all()
    jobs = db.query(Job).filter(
        Job.state == JobState.COMPLETED,
        Job.file_path.isnot(None)
    ).order_by(Job.created_at.desc()).all()
    result = []
    for j in jobs:
        filename = os.path.basename(j.file_path) if j.file_path else None
        result.append({
            "id": j.id,
            "original_url": j.original_url,
            "file_path": j.file_path,
            "filename": filename,
            "download_url": f"/downloads/{filename}" if filename else None,
            "state": j.state.value,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        })
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
