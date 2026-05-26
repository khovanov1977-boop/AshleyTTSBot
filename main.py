import asyncio
import logging
import os

import edge_tts

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

VOICE = "ru-RU-SvetlanaNeural"


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Отправьте текст, и я озвучу его."
    )


@dp.message()
async def tts_handler(message: Message):

    text = message.text

    file_name = "voice.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE
    )

    await communicate.save(file_name)

    audio = FSInputFile(file_name)

    await message.answer_voice(audio)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())