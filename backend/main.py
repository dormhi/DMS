from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.job import Job

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

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "DMS Backend is running."}

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    # Return all jobs, newest first
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
