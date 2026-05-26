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

user_settings = {}

# --- RU VOICES ONLY (3F + 3M) ---
VOICE_PRESETS = {
    "ru_female_1": "ru-RU-SvetlanaNeural",
    "ru_female_2": "ru-RU-DariyaNeural",
    "ru_female_3": "ru-RU-SvetlanaNeural",

    "ru_male_1": "ru-RU-DmitryNeural",
    "ru_male_2": "ru-RU-PavelNeural",
    "ru_male_3": "ru-RU-DmitryNeural",
}


# --- START ---
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Озвучка текста.\n\n"
        "/voice — выбрать голос\n"
        "/speed +20% / -20%\n"
        "/pitch +10Hz / -10Hz"
    )


# --- VOICE MENU ---
@dp.message(Command("voice"))
async def voice_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👩 Female 1", callback_data="v_ru_female_1")],
            [InlineKeyboardButton(text="👩 Female 2", callback_data="v_ru_female_2")],
            [InlineKeyboardButton(text="👩 Female 3", callback_data="v_ru_female_3")],

            [InlineKeyboardButton(text="👨 Male 1", callback_data="v_ru_male_1")],
            [InlineKeyboardButton(text="👨 Male 2", callback_data="v_ru_male_2")],
            [InlineKeyboardButton(text="👨 Male 3", callback_data="v_ru_male_3")],
        ]
    )

    await message.answer("Выберите голос:", reply_markup=keyboard)


# --- CALLBACK ---
@dp.callback_query(F.data.startswith("v_"))
async def voice_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    voice_key = callback.data.replace("v_", "")
    voice = VOICE_PRESETS.get(voice_key)

    if voice:
        settings = user_settings.get(user_id, {})
        settings["voice"] = voice
        settings.setdefault("rate", "+0%")
        settings.setdefault("pitch", "+0Hz")
        user_settings[user_id] = settings

        await callback.message.answer("Голос установлен")

    await callback.answer()


# --- SPEED ---
@dp.message(Command("speed"))
async def set_speed(message: Message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /speed +20% или -20%")
        return

    value = parts[1].strip()

    user_id = message.from_user.id
    settings = user_settings.get(user_id, {})

    settings["rate"] = value
    user_settings[user_id] = settings

    await message.answer(f"Скорость установлена: {value}")


# --- PITCH ---
@dp.message(Command("pitch"))
async def set_pitch(message: Message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Использование: /pitch +10Hz или -10Hz")
        return

    value = parts[1].strip()

    user_id = message.from_user.id
    settings = user_settings.get(user_id, {})

    settings["pitch"] = value
    user_settings[user_id] = settings

    await message.answer(f"Pitch установлен: {value}")


# --- TTS ---
@dp.message()
async def tts_handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    settings = user_settings.get(user_id, {})

    voice = settings.get("voice", DEFAULT_VOICE)
    rate = settings.get("rate", "+0%")
    pitch = settings.get("pitch", "+0Hz")

    text = message.text
    file_name = "voice.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )

    await communicate.save(file_name)

    audio = FSInputFile(file_name)
    await message.answer_voice(audio)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())