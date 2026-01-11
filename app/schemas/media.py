from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


class MediaBase(BaseModel):
    media_url: str
    media_type: str  # image, video


class MediaCreate(MediaBase):
    report_id: UUID4


class MediaUpdate(BaseModel):
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class MediaInDB(MediaBase):
    id: UUID4
    report_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class Media(MediaInDB):
    pass