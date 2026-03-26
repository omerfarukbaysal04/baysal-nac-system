from pydantic import BaseModel
from typing import Optional


# --- /auth endpoint ---
# FreeRADIUS rlm_rest bu endpoint'e JSON POST atar.
# Sifre duz metin gelir, bcrypt.checkpw() ile users tablosundaki hash ile karsilastirilir.

class AuthRequest(BaseModel):
    username: str
    password: str
    nas_ip: Optional[str] = None


class AuthResponse(BaseModel):
    result: str           # "Access-Accept" veya "Access-Reject"
    username: str
    group: Optional[str] = None


# --- /authorize endpoint ---
# Auth basariliysa FreeRADIUS hangi VLAN attribute'lerini donecegini sorar.

class AuthorizeRequest(BaseModel):
    username: str
    group: Optional[str] = None


class AuthorizeResponse(BaseModel):
    result: str
    attributes: dict      # Tunnel-Type, Tunnel-Medium-Type, Tunnel-Private-Group-Id


# --- /accounting endpoint ---

class AccountingRequest(BaseModel):
    session_id: str
    username: str
    nas_ip: str
    status_type: str      # Start | Interim-Update | Stop
    session_time: Optional[int] = None
    input_octets: Optional[int] = None
    output_octets: Optional[int] = None
    calling_station_id: Optional[str] = None
    framed_ip: Optional[str] = None


class AccountingResponse(BaseModel):
    result: str


# --- /users endpoint ---

class UserInfo(BaseModel):
    username: str
    group: str


# --- /sessions/active endpoint ---

class ActiveSession(BaseModel):
    session_id: str
    username: str
    nas_ip: str
    start_time: str