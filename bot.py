import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType
from aiogram.filters import CommandStart
from dotenv import load_dotenv


load_dotenv()
# Налаштування з змінних середовища
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # Наприклад: http://n8n:5678/webhook/audio-handler
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")  # Твій ID, щоб ніхто інший не ламав календар

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message( F.content_type == ContentType.VOICE)
async def handle_voice(message: Message):
    await message.answer("🎤 Отримав аудіо, обробляю...")

    # Завантаження файлу від Telegram
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Завантажуємо байти файлу
    file_bytes = await bot.download_file(file_path)

    # Відправка на n8n Webhook
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename='voice_message.ogg', content_type='audio/ogg')
        data.add_field('chat_id', str(message.chat.id))

        try:
            async with session.post(N8N_WEBHOOK_URL, data=data) as resp:
                if resp.status == 200:
                    await message.answer("✅ Відправлено в ядро (n8n).")
                else:
                    await message.answer(f"❌ Помилка n8n: {resp.status}")
        except Exception as e:
            await message.answer(f"❌ Помилка з'єднання: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio

    asyncio.run(main())