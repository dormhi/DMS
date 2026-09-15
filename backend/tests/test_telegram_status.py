from types import SimpleNamespace

from app.telegram import status


def test_download_progress_formats_known_size_and_throttles_updates(monkeypatch):
    sent_messages = []
    clock = [100.0]
    job = SimpleNamespace(chat_id="1", telegram_status_message_id=99)

    monkeypatch.setattr(status, "edit_status_message", lambda *args: sent_messages.append(args) or True)
    monkeypatch.setattr(status.time, "monotonic", lambda: clock[0])
    notifier = status.JobStatusNotifier(job)

    notifier.download_progress({
        "status": "downloading",
        "downloaded_bytes": 10,
        "total_bytes": 100,
        "speed": 10,
        "eta": 9,
    })
    clock[0] = 102.0
    notifier.download_progress({"status": "downloading", "downloaded_bytes": 12, "total_bytes": 100})
    clock[0] = 103.0
    notifier.download_progress({"status": "downloading", "downloaded_bytes": 15, "total_bytes": 100})

    assert len(sent_messages) == 2
    assert "%10" in sent_messages[0][2]
    assert "Kalan: ~9 sn" in sent_messages[0][2]
    assert "%15" in sent_messages[1][2]


def test_download_progress_without_total_shows_downloaded_bytes(monkeypatch):
    sent_messages = []
    job = SimpleNamespace(chat_id="1", telegram_status_message_id=99)
    monkeypatch.setattr(status, "edit_status_message", lambda *args: sent_messages.append(args) or True)

    status.JobStatusNotifier(job).download_progress({
        "status": "downloading",
        "downloaded_bytes": 1024 * 1024,
        "total_bytes": None,
    })

    assert "1.0 MB" in sent_messages[0][2]
    assert "%" not in sent_messages[0][2]


def test_status_update_failure_does_not_raise(monkeypatch):
    job = SimpleNamespace(chat_id="1", telegram_status_message_id=99)
    monkeypatch.setattr(status, "edit_status_message", lambda *args: False)

    assert status.JobStatusNotifier(job).update("test") is False
