import asyncio
import logging
import os
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from g4f.client import Client

# Токен твоего бота
TOKEN = ''

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем бота и клиент G4F
bot = Bot(token=TOKEN)
dp = Dispatcher()
g4f_client = Client()

# Стартовая команда с приветствием и картинкой
@dp.message(Command("start"))
async def start(message: types.Message):
    logger.info(f"Received start command from user {message.from_user.id}")
    try:
        base_dir = os.path.dirname(__file__)
        photo_path = os.path.join(base_dir, "welcome.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo, caption=f"👋 Привет, {message.from_user.first_name}! Пиши свой вопрос!")
    except Exception as e:
        logger.error(f"Error sending welcome message: {str(e)}")
        await message.answer(f"👋 Привет, {message.from_user.first_name}! Пиши свой вопрос!")

# Ответ на любое текстовое сообщение
@dp.message()
async def handle_text(message: types.Message):
    try:
        logger.info(f"Received message from user {message.from_user.id}: {message.text}")
        
        response = g4f_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message.text}]
        )
        
        logger.info(f"G4F response received: {response}")
        
        if response and response.choices and len(response.choices) > 0:
            answer_text = response.choices[0].message.content
            logger.info(f"Sending response to user: {answer_text[:100]}...")
            await message.answer(answer_text)
        else:
            logger.error("Empty response from G4F")
            await message.answer("❌ Не удалось получить ответ. Попробуйте еще раз.")
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await message.answer("❗️ Ошибка при получении ответа. Попробуйте позже.")

# Запуск
async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())