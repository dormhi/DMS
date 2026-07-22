import os
import asyncio
import logging
import time
from typing import Dict, List
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.db.session import SessionLocal, init_db
from app.db.models.job import Job, JobState
from app.worker.tasks import process_media_job

init_db()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
ALLOWED_IDS_RAW = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS: List[int] = []
if ALLOWED_IDS_RAW.strip():
    ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_IDS_RAW.split(",") if uid.strip().isdigit()]

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/data/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 3
_rate_limit_store: Dict[int, List[float]] = {}

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


class PrivateModeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if ALLOWED_USER_IDS and event.from_user:
            if event.from_user.id not in ALLOWED_USER_IDS:
                logging.warning(f"Unauthorized user {event.from_user.id} tried to use the bot")
                return
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if not event.from_user:
            return await handler(event, data)

        uid = event.from_user.id
        now = time.time()
        timestamps = _rate_limit_store.get(uid, [])
        timestamps = [ts for ts in timestamps if now - ts < RATE_LIMIT_WINDOW]

        if len(timestamps) >= RATE_LIMIT_MAX:
            await event.answer("⏳ Çok hızlı komut gönderiyorsun. Lütfen biraz bekle.")
            return

        timestamps.append(now)
        _rate_limit_store[uid] = timestamps
        return await handler(event, data)


dp.message.middleware(PrivateModeMiddleware())
dp.message.middleware(RateLimitMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "DMS'ye (Dormhi Media Server) hoş geldiniz!\n\n"
        "Komutlar:\n"
        "/download <url> - Verilen linkten video indirir.\n"
        "/jobs - Aktif işlerinizi listeler.\n"
        "/help - Sistem çalışma mantığını gösterir.\n"
        "Veya doğrudan bana bir video göndererek onarım/optimizasyon başlatabilirsiniz."
    )


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = (
        "🤖 *DMS (Dormhi Media Server) Çalışma Mantığı*\n\n"
        "Ben, cihazınızı yormadan videolarınızı sunucuda indirip, "
        "en iyi ve sorunsuz kaliteye getiren medya asistanınızım.\n\n"
        "📥 *İndirme (/download <link>)*\n"
        "1. Gönderdiğiniz linki analiz eder (Kick, YouTube vb.).\n"
        "2. Arka planda sunucuya indirir.\n"
        "3. İnen videoyu inceler, uyumsuzluk varsa düzeltir.\n\n"
        "🛠 *Onarım (Doğrudan Video Gönderme)*\n"
        "Eğer bana herhangi bir bozuk/uyumsuz video dosyası yollarsanız, "
        "bunu analiz edip donanım dostu, optimize edilmiş (h264/aac) formata "
        "sokarak kütüphaneye kaydederim.\n\n"
        "📊 *Durum Takibi (/jobs)*\n"
        "Kuyruktaki veya işlenen dosyalarınızın ne durumda olduğunu bu komutla görebilirsiniz."
    )
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("download"))
async def command_download_handler(message: Message) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Lütfen bir URL belirtin. Örnek: /download https://kick.com/...")
        return

    url = args[1].strip()

    db = SessionLocal()
    try:
        job = Job(original_url=url, chat_id=str(message.chat.id), state=JobState.PENDING)
        db.add(job)
        db.commit()
        db.refresh(job)

        process_media_job.delay(job.id)

        await message.answer(f"✅ İndirme görevi kuyruğa eklendi! (Job ID: {job.id})\nDurumu öğrenmek için /jobs yazabilirsiniz.")
    except Exception as e:
        await message.answer(f"Hata oluştu: {str(e)}")
    finally:
        db.close()


@dp.message(Command("jobs"))
async def command_jobs_handler(message: Message) -> None:
    db = SessionLocal()
    try:
        db.expire_all()
        jobs = db.query(Job).filter(Job.state.in_([JobState.PENDING, JobState.DOWNLOADING, JobState.PROCESSING])).all()
        if not jobs:
            await message.answer("Şu an aktif bir iş bulunmuyor.")
            return

        text = "Aktif İşler:\n"
        for j in jobs:
            text += f"ID: {j.id} | Durum: {j.state.value} | URL: {str(j.original_url)[:30]}...\n"

        await message.answer(text)
    finally:
        db.close()


@dp.message(F.video)
async def handle_video_upload(message: Message) -> None:
    await message.answer("Video alındı. Önce sunucuya indiriliyor, ardından işleme alınacak...")

    file_id = message.video.file_id
    filename = message.video.file_name or f"{file_id}.mp4"
    dest_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        tg_file = await bot.get_file(file_id)
        await bot.download_file(tg_file.file_path, dest_path)
    except Exception as e:
        logging.error(f"Failed to download Telegram file {file_id}: {e}")
        await message.answer(f"Dosya sunucudan indirilemedi: {str(e)}")
        return

    db = SessionLocal()
    try:
        job = Job(
            original_url=f"Telegram upload: {filename}",
            chat_id=str(message.chat.id),
            file_path=dest_path,
            state=JobState.PENDING,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        process_media_job.delay(job.id)

        await message.answer(f"✅ Onarım görevi kuyruğa eklendi! (Job ID: {job.id})")
    except Exception as e:
        await message.answer(f"Hata oluştu: {str(e)}")
    finally:
        db.close()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
