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

# --- DEFAULTS ---
DEFAULT_VOICE = "ru-RU-SvetlanaNeural"

# --- STORAGE ---
user_settings = {}

# --- VOICES ---
VOICE_PRESETS = {
    "ru_female": "ru-RU-SvetlanaNeural",
    "ru_male": "ru-RU-DmitryNeural",
    "en_female": "en-US-AriaNeural",
    "en_male": "en-US-GuyNeural",
}


# --- START ---
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Бот озвучивает текст.\n\n"
        "Команды:\n"
        "/voice — выбрать голос\n"
        "/speed +20% / -20%\n"
        "/pitch +10Hz / -10Hz"
    )


# --- VOICE MENU ---
@dp.message(Command("voice"))
async def voice_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Female", callback_data="v_ru_female")],
            [InlineKeyboardButton(text="🇷🇺 Male", callback_data="v_ru_male")],
            [InlineKeyboardButton(text="🇺🇸 Female", callback_data="v_en_female")],
            [InlineKeyboardButton(text="🇺🇸 Male", callback_data="v_en_male")],
        ]
    )

    await message.answer("Выберите голос:", reply_markup=keyboard)


# --- CALLBACK ---
@dp.callback_query(F.data.startswith("v_"))
async def voice_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    voice = VOICE_PRESETS.get(callback.data.replace("v_", ""))

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
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /speed +20% или -20%")
        return

    user_id = message.from_user.id
    settings = user_settings.get(user_id, {})

    settings["rate"] = args[1]
    user_settings[user_id] = settings

    await message.answer(f"Скорость: {args[1]}")


# --- PITCH ---
@dp.message(Command("pitch"))
async def set_pitch(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /pitch +10Hz или -10Hz")
        return

    user_id = message.from_user.id
    settings = user_settings.get(user_id, {})

    settings["pitch"] = args[1]
    user_settings[user_id] = settings

    await message.answer(f"Pitch: {args[1]}")


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


# --- RUN ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())