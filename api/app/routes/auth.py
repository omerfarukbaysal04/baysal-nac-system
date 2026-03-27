import bcrypt
from fastapi import APIRouter, HTTPException
from app import db
from app.models import AuthRequest

router = APIRouter()

@router.post("/auth")
async def authenticate(request: AuthRequest):
    """
    FreeRADIUS rlm_rest bu endpoint'e POST atar.
    Kullanici adi ve sifre gelir, bcrypt ile dogrulama yapilir.
    """

    # 1. Kullaniciyi veritabanindan cek
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT username, password_hash, groupname FROM users WHERE username = $1",
            request.username
        )

    # 2. Kullanici bulunamadiysa redis'e basarisiz denemeyi kaydet ve reject don
    if user is None:
        await _increment_fail_count(request.username)
        raise HTTPException(status_code=401, detail="User not found")

    # 3. Rate-limit kontrolu: ayni kullanici cok fazla basarisiz deneme yaptiysa engelle
    fail_count = await _get_fail_count(request.username)
    if fail_count >= 5:
        raise HTTPException(status_code=429, detail="Too many failed attempts")

    # 4. Sifre kontrolu: gelen duz metin sifre, veritabanindaki bcrypt hash ile karsilastirilir
    password_matches = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_matches:
        await _increment_fail_count(request.username)
        raise HTTPException(status_code=401, detail="Invalid password")

    # 5. Basarili giris: sayaci sifirla, Accept don (HTTP 200)
    await _reset_fail_count(request.username)
    return {"status": "success"}


# --- Yardimci fonksiyonlar (Redis rate-limiting) ---

RATE_LIMIT_KEY = "fail:{username}"
RATE_LIMIT_TTL = 300  # 5 dakika sonra sayac sifirlanir


async def _get_fail_count(username: str) -> int:
    key = RATE_LIMIT_KEY.format(username=username)
    val = await db.redis.get(key)
    return int(val) if val else 0


async def _increment_fail_count(username: str):
    key = RATE_LIMIT_KEY.format(username=username)
    await db.redis.incr(key)
    await db.redis.expire(key, RATE_LIMIT_TTL)


async def _reset_fail_count(username: str):
    key = RATE_LIMIT_KEY.format(username=username)
    await db.redis.delete(key)