import asyncio
import logging
import os

import edge_tts

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Голоса по умолчанию
DEFAULT_VOICE = "ru-RU-SvetlanaNeural"

# Хранилище выбора пользователя (в памяти)
user_voices = {}


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Отправь текст — я озвучу его.\n\n"
        "Команды:\n"
        "/voice female — женский голос\n"
        "/voice male — мужской голос"
    )


@dp.message(Command("voice"))
async def voice_handler(message: Message):
    global user_voices

    args = message.text.split()

    if len(args) < 2:
        await message.answer(
            "Использование:\n"
            "/voice female\n"
            "/voice male"
        )
        return

    choice = args[1].lower()

    if choice == "female":
        user_voices[message.from_user.id] = "ru-RU-SvetlanaNeural"
        await message.answer("Выбран женский голос")
    elif choice == "male":
        user_voices[message.from_user.id] = "ru-RU-DmitryNeural"
        await message.answer("Выбран мужской голос")
    else:
        await message.answer("Используй: female или male")


@dp.message()
async def tts_handler(message: Message):

    if not message.text:
        return

    text = message.text
    voice = user_voices.get(message.from_user.id, DEFAULT_VOICE)

    file_name = "voice.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(file_name)

    audio = FSInputFile(file_name)

    await message.answer_voice(audio)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())