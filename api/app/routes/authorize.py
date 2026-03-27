from fastapi import APIRouter, HTTPException
from app import db
from app.models import AuthorizeRequest

router = APIRouter()

# VLAN attribute degerleri sabit tanimli.
# Tunnel-Type 13 = VLAN (IEEE 802) [cite: 50]
# Tunnel-Medium-Type 6 = IEEE 802 (Ethernet) [cite: 50]
# Tunnel-Private-Group-Id = VLAN numarasi [cite: 50]
VLAN_MAP = {
    "admin":    {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "10"},
    "employee": {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "20"},
    "guest":    {"Tunnel-Type": "13", "Tunnel-Medium-Type": "6", "Tunnel-Private-Group-Id": "30"},
}

@router.post("/authorize")
async def authorize(request: AuthorizeRequest):
    """
    FreeRADIUS rlm_rest auth basariliysa bu endpoint'e POST atar.
    Kullanicinin grubuna gore hangi VLAN'a atanacagini doner[cite: 48, 51].
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

    # 2. Grup bulunamazsa veya tanimli degilse 403 donerek Reject et
    if not group or group not in VLAN_MAP:
        raise HTTPException(status_code=403, detail="Group not found or invalid")

    # 3. Gruba karsilik gelen VLAN attribute'lerini FreeRADIUS formatina cevir
    response_data = {}
    for key, value in VLAN_MAP[group].items():
        # 'reply:' on eki, FreeRADIUS'a bu degerleri dogrudan
        # Access-Accept paketi icine koymasini emreder.
        response_data[f"reply:{key}"] = value
    
    response_data["control:Auth-Type"] = "Rest"

    return response_data