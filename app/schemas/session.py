from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

class SessionBase(BaseModel):
    device_name: Optional[str] = None

class SessionCreate(SessionBase):
    user_id: UUID4
    refresh_token: str
    expires_at: datetime

class SessionUpdate(SessionBase):
    refresh_token: Optional[str] = None
    is_active: Optional[bool] = None
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class SessionInDB(SessionBase):
    id: UUID4
    user_id: UUID4
    refresh_token: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_used_at: datetime
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Session(SessionInDB):
    pass