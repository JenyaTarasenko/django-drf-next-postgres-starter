import asyncio
import os
# pyrefly: ignore [missing-import]
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден в .env")


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! 👋 Я Echo Bot.")


@dp.message()
async def echo_handler(message: Message):
    await message.answer(
        f"Ты написал: {message.text}"
    )


async def main():
    bot = Bot(token=TOKEN)

    print("🤖 Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())