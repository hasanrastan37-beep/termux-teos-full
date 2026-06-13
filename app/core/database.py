from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# تعیین پارامترهای اتصال بر اساس نوع دیتابیس
connect_args = {}
engine_kwargs = {
    "echo": settings.DEBUG,
}

if settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL: اضافه کردن pool settings
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
elif settings.DATABASE_URL.startswith("sqlite"):
    # SQLite: تنظیمات مخصوص
    connect_args = {"check_same_thread": False}
    # SQLite از pool_size پشتیبانی نمی‌کند

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
