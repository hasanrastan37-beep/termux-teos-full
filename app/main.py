import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("✅ ربات TEOS با موفقیت راه‌اندازی شد!")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("دستورات: /start - راه‌اندازی")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ایجاد جداول دیتابیس (در صورت نبود)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    
    # شروع polling (برای سادگی، webhook را فعلاً غیرفعال نگه دارید)
    asyncio.create_task(dp.start_polling(bot))
    logger.info("Bot started")
    yield
    await bot.session.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post(settings.BOT_WEBHOOK_PATH)
async def webhook(request: Request):
    if not settings.USE_WEBHOOK:
        return {"status": "webhook disabled"}
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}
