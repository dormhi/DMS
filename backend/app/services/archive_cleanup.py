"""Retention and disk-quota enforcement for the media archive."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.job import Job, JobState


logger = logging.getLogger(__name__)

RETENTION_DAYS = 7
MAX_ARCHIVE_BYTES = 5 * 1024 * 1024 * 1024
TERMINAL_STATES = (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED)


def _safe_file_path(file_path: str | None, download_dir: Path) -> Path | None:
    """Return a resolved archive path, never a path outside DOWNLOAD_DIR."""
    if not file_path:
        return None

    try:
        candidate = Path(file_path).resolve()
        root = download_dir.resolve()
        candidate.relative_to(root)
        return candidate
    except (OSError, ValueError):
        logger.warning("Ignoring job file outside archive directory: %s", file_path)
        return None


def _has_other_reference(db: Session, job: Job) -> bool:
    """Do not delete a physical file still referenced by another job."""
    return (
        db.query(Job.id)
        .filter(Job.id != job.id, Job.file_path == job.file_path)
        .first()
        is not None
    )


def _delete_job_and_file(db: Session, job: Job, download_dir: Path) -> bool:
    """Delete a terminal job; preserve its DB record when file deletion fails."""
    path = _safe_file_path(job.file_path, download_dir)

    if path and path.exists() and not _has_other_reference(db, job):
        try:
            path.unlink()
        except OSError:
            logger.exception("Could not delete archived media for job %s: %s", job.id, path)
            return False

    db.delete(job)
    db.commit()
    return True


def cleanup_archive(
    db: Session,
    download_dir: str | os.PathLike[str],
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """Remove expired terminal jobs and oldest completed media above the quota."""
    archive_dir = Path(download_dir)
    current_time = now or datetime.utcnow()
    cutoff = current_time - timedelta(days=RETENTION_DAYS)
    result = {"expired_jobs_deleted": 0, "quota_jobs_deleted": 0, "bytes_freed": 0}

    expired_jobs = (
        db.query(Job)
        .filter(Job.state.in_(TERMINAL_STATES), Job.updated_at < cutoff)
        .order_by(Job.updated_at.asc(), Job.id.asc())
        .all()
    )
    for job in expired_jobs:
        path = _safe_file_path(job.file_path, archive_dir)
        size = path.stat().st_size if path and path.is_file() else 0
        if _delete_job_and_file(db, job, archive_dir):
            result["expired_jobs_deleted"] += 1
            result["bytes_freed"] += size

    # One physical file is only counted once, even if bad historic data contains
    # multiple jobs with the same path.
    completed_jobs = (
        db.query(Job)
        .filter(Job.state == JobState.COMPLETED, Job.file_path.isnot(None))
        .order_by(Job.updated_at.asc(), Job.id.asc())
        .all()
    )
    unique_files: dict[Path, int] = {}
    quota_candidates: list[tuple[Job, Path, int]] = []
    for job in completed_jobs:
        path = _safe_file_path(job.file_path, archive_dir)
        if path and path.is_file() and path not in unique_files:
            size = path.stat().st_size
            unique_files[path] = size
            quota_candidates.append((job, path, size))

    total_size = sum(unique_files.values())
    for job, path, size in quota_candidates:
        if total_size <= MAX_ARCHIVE_BYTES:
            break

        if _delete_job_and_file(db, job, archive_dir):
            result["quota_jobs_deleted"] += 1
            if not path.exists():
                total_size -= size
                result["bytes_freed"] += size

    logger.info("Archive cleanup finished: %s", result)
    return result
