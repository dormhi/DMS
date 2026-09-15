from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.job import Job, JobState
from app.services import archive_cleanup


@pytest.fixture
def db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def make_job(db, *, state, path=None, updated_at=None):
    job = Job(
        original_url="https://example.test/video",
        file_path=str(path) if path else None,
        state=state,
        updated_at=updated_at or datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    return job


def test_expired_terminal_jobs_and_files_are_removed_but_active_jobs_remain(db, tmp_path):
    archive = tmp_path / "downloads"
    archive.mkdir()
    old_file = archive / "old.mp4"
    old_file.write_bytes(b"old")
    old_time = datetime.utcnow() - timedelta(days=8)

    completed = make_job(db, state=JobState.COMPLETED, path=old_file, updated_at=old_time)
    failed = make_job(db, state=JobState.FAILED, updated_at=old_time)
    cancelled = make_job(db, state=JobState.CANCELLED, updated_at=old_time)
    active = make_job(db, state=JobState.DOWNLOADING, updated_at=old_time)

    result = archive_cleanup.cleanup_archive(db, archive)

    assert result["expired_jobs_deleted"] == 3
    assert not old_file.exists()
    assert db.get(Job, completed.id) is None
    assert db.get(Job, failed.id) is None
    assert db.get(Job, cancelled.id) is None
    assert db.get(Job, active.id) is not None


def test_quota_removes_oldest_completed_files_first(db, tmp_path, monkeypatch):
    archive = tmp_path / "downloads"
    archive.mkdir()
    oldest_file = archive / "oldest.mp4"
    newest_file = archive / "newest.mp4"
    oldest_file.write_bytes(b"a" * 6)
    newest_file.write_bytes(b"b" * 5)
    now = datetime.utcnow()
    oldest = make_job(db, state=JobState.COMPLETED, path=oldest_file, updated_at=now - timedelta(hours=2))
    newest = make_job(db, state=JobState.COMPLETED, path=newest_file, updated_at=now - timedelta(hours=1))
    monkeypatch.setattr(archive_cleanup, "MAX_ARCHIVE_BYTES", 10)

    result = archive_cleanup.cleanup_archive(db, archive, now=now)

    assert result["quota_jobs_deleted"] == 1
    assert not oldest_file.exists()
    assert newest_file.exists()
    assert db.get(Job, oldest.id) is None
    assert db.get(Job, newest.id) is not None


@pytest.mark.parametrize("sizes", [(4, 5), (5, 5)])
def test_quota_keeps_media_at_or_below_limit(db, tmp_path, monkeypatch, sizes):
    archive = tmp_path / "downloads"
    archive.mkdir()
    first_file = archive / "first.mp4"
    second_file = archive / "second.mp4"
    first_file.write_bytes(b"a" * sizes[0])
    second_file.write_bytes(b"b" * sizes[1])
    first = make_job(db, state=JobState.COMPLETED, path=first_file)
    second = make_job(db, state=JobState.COMPLETED, path=second_file)
    monkeypatch.setattr(archive_cleanup, "MAX_ARCHIVE_BYTES", 10)

    result = archive_cleanup.cleanup_archive(db, archive)

    assert result["quota_jobs_deleted"] == 0
    assert db.get(Job, first.id) is not None
    assert db.get(Job, second.id) is not None


def test_quota_counts_a_shared_file_once(db, tmp_path, monkeypatch):
    archive = tmp_path / "downloads"
    archive.mkdir()
    shared_file = archive / "shared.mp4"
    shared_file.write_bytes(b"a" * 8)
    first = make_job(db, state=JobState.COMPLETED, path=shared_file)
    second = make_job(db, state=JobState.COMPLETED, path=shared_file)
    monkeypatch.setattr(archive_cleanup, "MAX_ARCHIVE_BYTES", 10)

    result = archive_cleanup.cleanup_archive(db, archive)

    assert result["quota_jobs_deleted"] == 0
    assert shared_file.exists()
    assert db.get(Job, first.id) is not None
    assert db.get(Job, second.id) is not None


def test_quota_ignores_missing_files_and_continues_after_delete_error(db, tmp_path, monkeypatch):
    archive = tmp_path / "downloads"
    archive.mkdir()
    blocked_file = archive / "blocked.mp4"
    valid_file = archive / "valid.mp4"
    blocked_file.write_bytes(b"a" * 6)
    valid_file.write_bytes(b"b" * 6)
    now = datetime.utcnow()
    blocked = make_job(db, state=JobState.COMPLETED, path=blocked_file, updated_at=now - timedelta(hours=2))
    valid = make_job(db, state=JobState.COMPLETED, path=valid_file, updated_at=now - timedelta(hours=1))
    make_job(db, state=JobState.COMPLETED, path=archive / "missing.mp4", updated_at=now)
    monkeypatch.setattr(archive_cleanup, "MAX_ARCHIVE_BYTES", 5)
    original_unlink = archive_cleanup.Path.unlink

    def fail_for_blocked(path):
        if path == blocked_file:
            raise OSError("permission denied")
        return original_unlink(path)

    monkeypatch.setattr(archive_cleanup.Path, "unlink", fail_for_blocked)

    archive_cleanup.cleanup_archive(db, archive, now=now)

    assert blocked_file.exists()
    assert not valid_file.exists()
    assert db.get(Job, blocked.id) is not None
    assert db.get(Job, valid.id) is None
