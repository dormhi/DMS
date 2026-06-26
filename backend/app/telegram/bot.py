import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from app.db.session import SessionLocal
from app.db.models.job import Job, JobState
from app.worker.tasks import process_media_job

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        "DMS'ye (Dormhi Media Server) hoş geldiniz!\n\n"
        "Komutlar:\n"
        "/download <url> - Verilen linkten video indirir.\n"
        "/jobs - Aktif işlerinizi listeler.\n"
        "/help - Sistem çalışma mantığını gösterir.\n"
        "Veya doğrudan bana bir video göndererek onarım/optimizasyon başlatabilirsiniz."
    )

@dp.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
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
async def command_download_handler(message: types.Message) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Lütfen bir URL belirtin. Örnek: /download https://kick.com/...")
        return
        
    url = args[1].strip()
    
    db = SessionLocal()
    try:
        job = Job(original_url=url, state=JobState.PENDING)
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Trigger Celery Task
        process_media_job.delay(job.id)
        
        await message.answer(f"✅ İndirme görevi kuyruğa eklendi! (Job ID: {job.id})\nDurumu öğrenmek için /jobs yazabilirsiniz.")
    except Exception as e:
        await message.answer(f"Hata oluştu: {str(e)}")
    finally:
        db.close()

@dp.message(Command("jobs"))
async def command_jobs_handler(message: types.Message) -> None:
    db = SessionLocal()
    try:
        # Fetch active jobs
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
async def handle_video_upload(message: types.Message) -> None:
    # A user uploaded a video for repair/optimization
    file_id = message.video.file_id
    await message.answer("Video alındı. Onarım/Optimizasyon kuyruğuna ekleniyor...")
    
    db = SessionLocal()
    try:
        job = Job(original_url=f"tg_file://{file_id}", state=JobState.PENDING)
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
