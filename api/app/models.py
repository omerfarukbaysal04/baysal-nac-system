from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any

# FreeRADIUS JSON gonderirken degerleri liste icinde gonderir: {"User-Name": ["admin"]}
# Bu base sinif, gelen listeleri tekil metne cevirerek Pydantic'in isini kolaylastirir.
class FreeRadiusBaseModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def flatten_lists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v[0] if isinstance(v, list) and v else v for k, v in data.items()}
        return data

# --- /auth endpoint ---
class AuthRequest(FreeRadiusBaseModel):
    username: str = Field(alias="User-Name")
    password: str = Field(alias="User-Password", default="")
    nas_ip: Optional[str] = Field(alias="NAS-IP-Address", default=None)

# --- /authorize endpoint ---
class AuthorizeRequest(FreeRadiusBaseModel):
    username: str = Field(alias="User-Name")
    group: Optional[str] = Field(alias="SQL-Group", default=None)

# --- /accounting endpoint ---
class AccountingRequest(FreeRadiusBaseModel):
    session_id: str = Field(alias="Acct-Session-Id")
    username: str = Field(alias="User-Name")
    nas_ip: str = Field(alias="NAS-IP-Address")
    status_type: str = Field(alias="Acct-Status-Type")      # Start | Interim-Update | Stop
    session_time: Optional[int] = Field(alias="Acct-Session-Time", default=None)
    input_octets: Optional[int] = Field(alias="Acct-Input-Octets", default=None)
    output_octets: Optional[int] = Field(alias="Acct-Output-Octets", default=None)
    calling_station_id: Optional[str] = Field(alias="Calling-Station-Id", default=None)
    framed_ip: Optional[str] = Field(alias="Framed-IP-Address", default=None)

# --- GET endpointleri icin (FreeRADIUS atmaz, biz sorgulariz) ---
class UserInfo(BaseModel):
    username: str
    group: str

class ActiveSession(BaseModel):
    session_id: str
    username: str
    nas_ip: str
    start_time: str