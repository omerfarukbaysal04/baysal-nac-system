from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import db
from app.routes import auth, authorize, accounting
from app.routes.auth import router as auth_router
from app.routes.authorize import router as authorize_router
from app.routes.accounting import router as accounting_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama baslarken baglantilari ac
    await db.init_db()
    await db.init_redis()
    yield
    # Uygulama kapanirken baglantilari kapat
    await db.close_db()
    await db.close_redis()


app = FastAPI(title="Baysal NAC API", lifespan=lifespan)

# Route'lari kaydet
app.include_router(auth_router)
app.include_router(authorize_router)
app.include_router(accounting_router)


@app.get("/health")
async def health():
    """docker-compose healthcheck bu endpoint'i kullanir."""
    return {"status": "ok"}


@app.get("/users")
async def get_users():
    """Tum kullanicilari ve gruplarini doner."""
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT u.username, u.groupname FROM radusergroup u ORDER BY u.username"
        )
    return [{"username": r["username"], "group": r["groupname"]} for r in rows]


@app.get("/sessions/active")
async def get_active_sessions():
    """Redis'ten aktif oturumlari doner."""
    keys = await db.redis.keys("session:*")
    sessions = []
    for key in keys:
        data = await db.redis.hgetall(key)
        sessions.append(data)
    return sessions