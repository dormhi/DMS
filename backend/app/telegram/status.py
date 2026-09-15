"""Low-overhead Telegram status updates used by synchronous worker tasks."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests


logger = logging.getLogger(__name__)
UPDATE_INTERVAL_SECONDS = 5
SIGNIFICANT_PERCENT_CHANGE = 5


def format_bytes(value: Any) -> str:
    if not isinstance(value, (int, float)) or value < 0:
        return "?"
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return "?"


def format_eta(value: Any) -> str | None:
    if not isinstance(value, (int, float)) or value < 0:
        return None
    seconds = int(value)
    if seconds < 60:
        return f"~{seconds} sn"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"~{minutes} dk {seconds} sn"
    hours, minutes = divmod(minutes, 60)
    return f"~{hours} sa {minutes} dk"


def safe_error_summary(error: Exception | str) -> str:
    """Keep user-facing errors useful without sending unbounded provider output."""
    summary = " ".join(str(error).split())
    return (summary[:497] + "...") if len(summary) > 500 else summary


def edit_status_message(chat_id: str, message_id: int, text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.warning("Cannot update Telegram status: TELEGRAM_BOT_TOKEN is missing")
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/editMessageText",
            json={"chat_id": chat_id, "message_id": message_id, "text": text},
            timeout=15,
        )
        if response.ok:
            return True
        logger.warning("Telegram status update failed: %s", response.text)
    except requests.RequestException:
        logger.exception("Telegram status update request failed")
    return False


class JobStatusNotifier:
    """Edits one Telegram message and throttles frequent yt-dlp progress hooks."""

    def __init__(self, job: Any):
        self.chat_id = job.chat_id
        self.message_id = job.telegram_status_message_id
        self.last_update_at = 0.0
        self.last_percent: int | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.chat_id and self.message_id)

    def update(self, text: str) -> bool:
        if not self.enabled:
            return False
        updated = edit_status_message(str(self.chat_id), int(self.message_id), text)
        if updated:
            self.last_update_at = time.monotonic()
        return updated

    def download_progress(self, progress: dict[str, Any]) -> None:
        if not self.enabled or progress.get("status") not in {"downloading", "finished"}:
            return

        downloaded = progress.get("downloaded_bytes", 0)
        total = progress.get("total_bytes") or progress.get("total_bytes_estimate")
        percent = int(downloaded / total * 100) if total and downloaded is not None else None
        now = time.monotonic()
        significant_change = (
            percent is not None
            and (self.last_percent is None or percent >= self.last_percent + SIGNIFICANT_PERCENT_CHANGE)
        )
        if now - self.last_update_at < UPDATE_INTERVAL_SECONDS and not significant_change:
            return

        details = [f"📥 İndiriliyor: {format_bytes(downloaded)}"]
        if percent is not None:
            details[0] = f"📥 İndiriliyor: %{min(percent, 100)}"
            details.append(f"{format_bytes(downloaded)} / {format_bytes(total)}")
        speed = progress.get("speed")
        if speed:
            details.append(f"{format_bytes(speed)}/sn")
        eta = format_eta(progress.get("eta"))
        if eta:
            details.append(f"Kalan: {eta}")

        if self.update("\n".join(details)) and percent is not None:
            self.last_percent = percent
