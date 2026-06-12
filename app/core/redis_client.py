import asyncio
from typing import Optional, Any

class FakeRedis:
    async def get(self, key: str) -> Optional[str]:
        return None
    async def set(self, key: str, value: Any, ex: int = None) -> bool:
        return True
    async def setex(self, key: str, seconds: int, value: Any) -> bool:
        return True
    async def incr(self, key: str) -> int:
        return 1
    async def delete(self, key: str) -> int:
        return 1
    async def exists(self, key: str) -> int:
        return 0
    async def expire(self, key: str, seconds: int) -> bool:
        return True
    async def ttl(self, key: str) -> int:
        return -1
    async def lpush(self, key: str, value: str) -> int:
        return 1
    async def ping(self) -> bool:
        return True

redis_client = FakeRedis()

async def init_redis():
    return redis_client

async def close_redis():
    pass
