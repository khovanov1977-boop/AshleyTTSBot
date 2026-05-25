import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Бот работает.")


@dp.message()
async def echo_handler(message: Message):
    await message.answer(
        f"Вы написали:\n{message.text}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())