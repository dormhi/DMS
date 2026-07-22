import os
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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

# ─── Auth (hardcoded) ───────────────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
JWT_SECRET = "dms_hardcoded_secret_key_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ─── Public endpoints ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "DMS Backend is running."}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

# ─── Protected endpoints ───────────────────────────────────────────

class UrlSubmit(BaseModel):
    url: str

@app.post("/api/jobs/submit")
def submit_job(body: UrlSubmit, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """Submit a URL for download and processing."""
    from app.worker.tasks import process_media_job

    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    job = Job(original_url=url, state=JobState.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    process_media_job.delay(job.id)

    return {"id": job.id, "message": "Job submitted successfully"}

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
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
def get_completed_jobs(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
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

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.file_path and os.path.exists(job.file_path):
        os.remove(job.file_path)

    db.delete(job)
    db.commit()
    return {"message": f"Job #{job_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
