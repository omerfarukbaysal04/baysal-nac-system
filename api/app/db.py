import os
import asyncpg
import redis.asyncio as aioredis

# Bu modül uygulama boyunca tek bir baglanti havuzu tutar.
# Her istek geldiginde yeni baglanti acmak yerine havuzdan alinir, islem
# bitince geri birakilir. Bu hem performans hem de kaynak yonetimi acisindan dogru yaklasim.

DB_DSN = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# main.py'daki lifespan fonksiyonu bu degiskenleri doldurur
pool: asyncpg.Pool | None = None
redis: aioredis.Redis | None = None


async def init_db():
    """Uygulama baslarken cagrilir. Baglanti havuzunu olusturur."""
    global pool
    pool = await asyncpg.create_pool(dsn=DB_DSN, min_size=2, max_size=10)


async def close_db():
    """Uygulama kapanirken cagrilir."""
    global pool
    if pool:
        await pool.close()


async def init_redis():
    """Redis baglantisini olusturur."""
    global redis
    redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


async def close_redis():
    """Redis baglantisini kapatir."""
    global redis
    if redis:
        await redis.aclose()