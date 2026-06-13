from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# تنظیمات اتصال بر اساس نوع دیتابیس
connect_args = {}
engine_kwargs = {"echo": settings.DEBUG}

if settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL از pooling پشتیبانی می‌کند
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
elif settings.DATABASE_URL.startswith("sqlite"):
    # SQLite نیاز به این تنظیم دارد و pooling را قبول نمی‌کند
    connect_args = {"check_same_thread": False}
    # حذف pool_size و max_overflow از engine_kwargs
    engine_kwargs.pop("pool_size", None)
    engine_kwargs.pop("max_overflow", None)

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
