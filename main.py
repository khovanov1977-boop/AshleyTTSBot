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

STYLE_PRESETS = {
    "calm": {
        "name": "😌 Спокойный",
        "rate": "-20%",
        "pitch": "-10Hz",
        "volume": "-10%",
    },
    "normal": {
        "name": "🙂 Обычный",
        "rate": "+0%",
        "pitch": "+0Hz",
        "volume": "+0%",
    },
    "energetic": {
        "name": "⚡ Энергичный",
        "rate": "+25%",
        "pitch": "+10Hz",
        "volume": "+10%",
    },
    "announcer": {
        "name": "📺 Диктор",
        "rate": "-10%",
        "pitch": "+0Hz",
        "volume": "+15%",
    },
    "tender": {
        "name": "❤️ Нежный",
        "rate": "-15%",
        "pitch": "+12Hz",
        "volume": "-15%",
    },
    "happy": {
        "name": "😄 Радостный",
        "rate": "+20%",
        "pitch": "+15Hz",
        "volume": "+15%",
    },
    "worried": {
        "name": "😟 Взволнованный",
        "rate": "+30%",
        "pitch": "+20Hz",
        "volume": "+10%",
    },
    "scared": {
        "name": "😨 Испуганный",
        "rate": "+40%",
        "pitch": "+30Hz",
        "volume": "+5%",
    },
    "passionate": {
        "name": "🔥 Страстный",
        "rate": "+10%",
        "pitch": "-5Hz",
        "volume": "+25%",
    },
    "playful": {
        "name": "😉 Игривый",
        "rate": "+20%",
        "pitch": "+25Hz",
        "volume": "+5%",
    },
    "serious": {
        "name": "🎓 Серьёзный",
        "rate": "-15%",
        "pitch": "-15Hz",
        "volume": "+0%",
    },
    "sad": {
        "name": "😔 Грустный",
        "rate": "-25%",
        "pitch": "-20Hz",
        "volume": "-20%",
    },
}


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Бот озвучивает текст голосом.\n\n"
        "/voice — выбрать голос\n"
        "/settings — стиль чтения"
    )


@dp.message(Command("voice"))
async def voice_menu(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👩 Светлана",
                    callback_data="voice_female",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨 Дмитрий",
                    callback_data="voice_male",
                )
            ],
        ]
    )

    await message.answer(
        "Выберите голос:",
        reply_markup=keyboard,
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
    settings.setdefault("volume", "+0%")

    user_settings[user_id] = settings

    await callback.message.answer("Голос установлен")
    await callback.answer()


@dp.message(Command("settings"))
async def settings_menu(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="😌 Спокойный",
                    callback_data="style_calm",
                ),
                InlineKeyboardButton(
                    text="🙂 Обычный",
                    callback_data="style_normal",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚡ Энергичный",
                    callback_data="style_energetic",
                ),
                InlineKeyboardButton(
                    text="📺 Диктор",
                    callback_data="style_announcer",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Нежный",
                    callback_data="style_tender",
                ),
                InlineKeyboardButton(
                    text="😄 Радостный",
                    callback_data="style_happy",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="😟 Взволнованный",
                    callback_data="style_worried",
                ),
                InlineKeyboardButton(
                    text="😨 Испуганный",
                    callback_data="style_scared",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Страстный",
                    callback_data="style_passionate",
                ),
                InlineKeyboardButton(
                    text="😉 Игривый",
                    callback_data="style_playful",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Серьёзный",
                    callback_data="style_serious",
                ),
                InlineKeyboardButton(
                    text="😔 Грустный",
                    callback_data="style_sad",
                ),
            ],
        ]
    )

    await message.answer(
        "Выберите стиль чтения:",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data.startswith("style_"))
async def style_callback(callback: CallbackQuery):

    user_id = callback.from_user.id

    style_key = callback.data.replace("style_", "")
    preset = STYLE_PRESETS.get(style_key)

    if not preset:
        await callback.answer()
        return

    settings = user_settings.get(user_id, {})

    settings["rate"] = preset["rate"]
    settings["pitch"] = preset["pitch"]
    settings["volume"] = preset["volume"]

    user_settings[user_id] = settings

    await callback.message.answer(
        f"Стиль установлен: {preset['name']}"
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
    volume = settings.get("volume", "+0%")

    file_name = f"voice_{user_id}.mp3"

    try:
        communicate = edge_tts.Communicate(
            text=message.text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
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