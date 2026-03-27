from fastapi import APIRouter
from datetime import datetime, timezone
from app import db
from app.models import AccountingRequest, AccountingResponse

router = APIRouter()


@router.post("/accounting", response_model=AccountingResponse)
async def accounting(request: AccountingRequest):
    """
    FreeRADIUS rlm_rest her Accounting-Request paketinde bu endpoint'e POST atar.
    status_type degeri Start, Interim-Update veya Stop olabilir.
    Her durum icin farkli bir islem yapilir.
    """

    if request.status_type == "Start":
        await _handle_start(request)

    elif request.status_type == "Interim-Update":
        await _handle_interim(request)

    elif request.status_type == "Stop":
        await _handle_stop(request)

    return AccountingResponse(result="ok")


# --- Yardimci fonksiyonlar ---

async def _handle_start(req: AccountingRequest):
    """
    Oturum basladi: PostgreSQL'e yeni kayit ac, Redis'e aktif oturum olarak ekle.
    """
    now = datetime.now(timezone.utc)

    async with db.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO radacct
                (acctsessionid, username, nasipaddress, acctstarttime,
                 callingstationid, framedipaddress)
            VALUES ($1, $2, $3::inet, $4, $5, $6::inet)
            """,
            req.session_id,
            req.username,
            req.nas_ip,
            now,
            req.calling_station_id or "",
            req.framed_ip,
        )

    # Redis'e aktif oturum olarak cache'le
    # key: session:<session_id>  value: hash (username, nas_ip, start_time)
    session_key = f"session:{req.session_id}"
    await db.redis.hset(session_key, mapping={
        "session_id": req.session_id,
        "username":   req.username,
        "nas_ip":     req.nas_ip,
        "start_time": now.isoformat(),
    })
    # 24 saat sonra otomatik temizlensin (zombi oturumlara karsi)
    await db.redis.expire(session_key, 86400)


async def _handle_interim(req: AccountingRequest):
    """
    Ara guncelleme: PostgreSQL'deki oturum kaydini guncelle.
    Aktarilan veri miktarini ve guncelleme zamanini yaz.
    """
    now = datetime.now(timezone.utc)

    async with db.pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE radacct
            SET
                acctupdatetime   = $1,
                acctsessiontime  = $2,
                acctinputoctets  = $3,
                acctoutputoctets = $4
            WHERE acctsessionid = $5
            """,
            now,
            req.session_time,
            req.input_octets,
            req.output_octets,
            req.session_id,
        )


async def _handle_stop(req: AccountingRequest):
    """
    Oturum bitti: PostgreSQL'deki kaydi kapat, Redis'ten sil.
    """
    now = datetime.now(timezone.utc)

    async with db.pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE radacct
            SET
                acctstoptime     = $1,
                acctsessiontime  = $2,
                acctinputoctets  = $3,
                acctoutputoctets = $4
            WHERE acctsessionid = $5
            """,
            now,
            req.session_time,
            req.input_octets,
            req.output_octets,
            req.session_id,
        )

    # Aktif oturumlar listesinden cikar
    await db.redis.delete(f"session:{req.session_id}")