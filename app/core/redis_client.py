class FakeRedis:
    async def get(self, key): return None
    async def set(self, key, value, ex=None): return True
    async def setex(self, key, seconds, value): return True
    async def incr(self, key): return 1
    async def delete(self, key): return 1
    async def exists(self, key): return 0
    async def expire(self, key, seconds): return True
    async def ttl(self, key): return -1
    async def lpush(self, key, value): return 1
    async def ping(self): return True

redis_client = FakeRedis()

async def init_redis():
    return redis_client

async def close_redis():
    pass
