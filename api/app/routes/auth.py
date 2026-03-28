import bcrypt
from fastapi import APIRouter
from app import db
from app.models import AuthRequest

router = APIRouter()

VLAN_MAP = {
    "admin":    "10",
    "employee": "20",
    "guest":    "30",
}

@router.post("/auth")
async def authenticate(request: AuthRequest):
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT username, password_hash, groupname FROM users WHERE username = $1",
            request.username
        )

    if user is None:
        await _increment_fail_count(request.username)
        return {}

    fail_count = await _get_fail_count(request.username)
    if fail_count >= 5:
        return {}

    password_matches = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_matches:
        await _increment_fail_count(request.username)
        return {}

    await _reset_fail_count(request.username)
    vlan = VLAN_MAP.get(user["groupname"], "30")
    return {
        "reply:Tunnel-Type": "13",
        "reply:Tunnel-Medium-Type": "6",
        "reply:Tunnel-Private-Group-Id": vlan
    }


RATE_LIMIT_KEY = "fail:{username}"
RATE_LIMIT_TTL = 300

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