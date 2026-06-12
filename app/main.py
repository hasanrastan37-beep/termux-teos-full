import asyncio
import logging
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.logging_setup import setup_logging
from app.bot.dispatcher import create_dispatcher, bot as bot_instance
from app.api.main import app as api_app
from app.workers.scheduler import start_scheduler
from app.services.backup_service import BackupService
from app.services.auto_update_service import AutoUpdateService

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TEOS...")
    if settings.USE_WEBHOOK:
        await bot_instance.set_webhook(
            url=f"{settings.BOT_WEBHOOK_URL}{settings.BOT_WEBHOOK_PATH}",
            allowed_updates=Update.get_all_updates_types()
        )
    else:
        asyncio.create_task(start_polling())
    start_scheduler()
    BackupService().schedule_backup()
    if settings.AUTO_UPDATE_ENABLED:
        AutoUpdateService().check_updates()
    yield
    # Shutdown
    logger.info("Shutting down TEOS...")
    if settings.USE_WEBHOOK:
        await bot_instance.delete_webhook()
    await bot_instance.session.close()
    await engine.dispose()

async def start_polling():
    dp = create_dispatcher()
    await dp.start_polling(bot_instance, skip_updates=True)

app = FastAPI(
    title="TEOS API",
    description="Enterprise Operating System for Telegram",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/api", api_app)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post(settings.BOT_WEBHOOK_PATH)
async def bot_webhook(request: Request) -> dict:
    if not settings.USE_WEBHOOK:
        return {"status": "disabled"}
    update = Update.model_validate(await request.json(), context={"bot": bot_instance})
    dp = create_dispatcher()
    await dp.feed_update(bot_instance, update)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(settings.API_PORT)
    uvicorn.run(app, host="0.0.0.0", port=port)
