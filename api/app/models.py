from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any


class FreeRadiusBaseModel(BaseModel):
    model_config = {"populate_by_name": True}

    @model_validator(mode='before')
    @classmethod
    def flatten_fr_attributes(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        cleaned = {}
        for k, v in data.items():
            # Format 1: ["admin1"]  -> düz liste
            if isinstance(v, list) and v:
                cleaned[k] = v[0]
            # Format 2: {"type": "string", "value": ["admin1"]}  -> rlm_rest objesi
            elif isinstance(v, dict) and "value" in v:
                vals = v["value"]
                cleaned[k] = vals[0] if isinstance(vals, list) and vals else vals
            else:
                cleaned[k] = v
        return cleaned


class AuthRequest(FreeRadiusBaseModel):
    username: str = Field(alias="User-Name")
    password: str = Field(alias="User-Password", default="")
    nas_ip: Optional[str] = Field(alias="NAS-IP-Address", default=None)


class AuthorizeRequest(FreeRadiusBaseModel):
    username: str = Field(alias="User-Name")
    group: Optional[str] = Field(alias="SQL-Group", default=None)


class AccountingRequest(FreeRadiusBaseModel):
    session_id: str = Field(alias="Acct-Session-Id")
    username: str = Field(alias="User-Name")
    nas_ip: str = Field(alias="NAS-IP-Address")
    status_type: str = Field(alias="Acct-Status-Type")
    session_time: Optional[int] = Field(alias="Acct-Session-Time", default=None)
    input_octets: Optional[int] = Field(alias="Acct-Input-Octets", default=None)
    output_octets: Optional[int] = Field(alias="Acct-Output-Octets", default=None)
    calling_station_id: Optional[str] = Field(alias="Calling-Station-Id", default=None)
    framed_ip: Optional[str] = Field(alias="Framed-IP-Address", default=None)


class UserInfo(BaseModel):
    username: str
    group: str


class ActiveSession(BaseModel):
    session_id: str
    username: str
    nas_ip: str
    start_time: str