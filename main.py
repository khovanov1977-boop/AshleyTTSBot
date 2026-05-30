import asyncio
import logging
import os

import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    FSInputFile,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

DEFAULT_VOICE = "ru-RU-SvetlanaNeural"

user_settings = {}

VOICE_PRESETS = {
    "female": "ru-RU-SvetlanaNeural",
    "male": "ru-RU-DmitryNeural",
}


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Бот озвучивает текст голосом.\n\n"
        "/voice — выбрать голос\n"
        "/settings — настройки голоса"
    )


@dp.message(Command("voice"))
async def voice_menu(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👩 Светлана",
                    callback_data="voice_female"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨 Дмитрий",
                    callback_data="voice_male"
                )
            ],
        ]
    )

    await message.answer(
        "Выберите голос:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("voice_"))
async def voice_callback(callback: CallbackQuery):

    user_id = callback.from_user.id

    voice_key = callback.data.replace("voice_", "")
    voice = VOICE_PRESETS.get(voice_key)

    settings = user_settings.get(user_id, {})

    settings["voice"] = voice
    settings.setdefault("rate", "+0%")
    settings.setdefault("pitch", "+0Hz")

    user_settings[user_id] = settings

    await callback.message.answer("Голос установлен")
    await callback.answer()


@dp.message(Command("settings"))
async def settings_menu(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐢 Медленно",
                    callback_data="speed_slow"
                ),
                InlineKeyboardButton(
                    text="⚖️ Нормально",
                    callback_data="speed_normal"
                ),
                InlineKeyboardButton(
                    text="🚀 Быстро",
                    callback_data="speed_fast"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔉 Ниже",
                    callback_data="pitch_low"
                ),
                InlineKeyboardButton(
                    text="🔊 Обычный",
                    callback_data="pitch_normal"
                ),
                InlineKeyboardButton(
                    text="📢 Выше",
                    callback_data="pitch_high"
                ),
            ],
        ]
    )

    await message.answer(
        "Настройки голоса:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("speed_"))
async def speed_callback(callback: CallbackQuery):

    user_id = callback.from_user.id

    settings = user_settings.get(user_id, {})

    speed_map = {
        "speed_slow": "-30%",
        "speed_normal": "+0%",
        "speed_fast": "+30%",
    }

    settings["rate"] = speed_map[callback.data]

    user_settings[user_id] = settings

    await callback.message.answer(
        f"Скорость установлена: {settings['rate']}"
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("pitch_"))
async def pitch_callback(callback: CallbackQuery):

    user_id = callback.from_user.id

    settings = user_settings.get(user_id, {})

    pitch_map = {
        "pitch_low": "-20Hz",
        "pitch_normal": "+0Hz",
        "pitch_high": "+20Hz",
    }

    settings["pitch"] = pitch_map[callback.data]

    user_settings[user_id] = settings

    await callback.message.answer(
        f"Тон установлен: {settings['pitch']}"
    )

    await callback.answer()


@dp.message()
async def tts_handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id

    settings = user_settings.get(user_id, {})

    voice = settings.get("voice", DEFAULT_VOICE)
    rate = settings.get("rate", "+0%")
    pitch = settings.get("pitch", "+0Hz")

    file_name = f"voice_{user_id}.mp3"

    try:
        communicate = edge_tts.Communicate(
            text=message.text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )

        await communicate.save(file_name)

        audio = FSInputFile(file_name)

        await message.answer_voice(audio)

    except Exception as e:
        logging.exception(e)
        await message.answer(
            "Ошибка синтеза речи. Попробуйте еще раз."
        )

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())