import asyncio
import logging
import os

import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

DEFAULT_VOICE = "ru-RU-SvetlanaNeural"

user_voices = {}


# --- START ---
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Отправь текст — я озвучу его.\n\n"
        "Команда:\n"
        "/voice — выбрать голос"
    )


# --- VOICE MENU ---
@dp.message(Command("voice"))
async def voice_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👩 Female (Svetlana)",
                    callback_data="voice_female"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨 Male (Dmitry)",
                    callback_data="voice_male"
                )
            ]
        ]
    )

    await message.answer("Выбери голос:", reply_markup=keyboard)


# --- CALLBACK HANDLER ---
@dp.callback_query(F.data.startswith("voice_"))
async def voice_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    if callback.data == "voice_female":
        user_voices[user_id] = "ru-RU-SvetlanaNeural"
        await callback.message.answer("Выбран женский голос")

    elif callback.data == "voice_male":
        user_voices[user_id] = "ru-RU-DmitryNeural"
        await callback.message.answer("Выбран мужской голос")

    await callback.answer()


# --- TTS ---
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