from fastapi import APIRouter
from app import db
from app.models import AuthorizeRequest, AuthorizeResponse

router = APIRouter()

# VLAN attribute degerleri sabit tanimli.
# Tunnel-Type 13 = VLAN (IEEE 802)
# Tunnel-Medium-Type 6 = IEEE 802 (Ethernet)
# Tunnel-Private-Group-Id = VLAN numarasi
VLAN_MAP = {
    "admin":    {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "10"},
    "employee": {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "20"},
    "guest":    {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "30"},
}


@router.post("/authorize", response_model=AuthorizeResponse)
async def authorize(request: AuthorizeRequest):
    """
    FreeRADIUS rlm_rest auth basariliysa bu endpoint'e POST atar.
    Kullanicinin grubuna gore hangi VLAN'a atanacagini doner.
    """

    # 1. Grub bilgisi request'te geldiyse kullan, gelmediyse DB'den cek
    group = request.group
    if not group:
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT groupname FROM radusergroup WHERE username = $1 ORDER BY priority LIMIT 1",
                request.username
            )
        group = row["groupname"] if row else None

    # 2. Grup bulunamazsa veya tanimli degilse reject
    if not group or group not in VLAN_MAP:
        return AuthorizeResponse(result="Access-Reject", attributes={})

    # 3. Gruba karsilik gelen VLAN attribute'lerini don
    return AuthorizeResponse(
        result="Access-Accept",
        attributes=VLAN_MAP[group]
    )