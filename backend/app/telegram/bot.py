import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# TODO: Day 5 - Move to config/env
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer("DMS'ye hoş geldiniz! Sistem durumu: Aktif.")

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
