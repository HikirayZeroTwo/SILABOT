import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers import router


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    print("🚀 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())