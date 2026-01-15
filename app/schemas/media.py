from pydantic import BaseModel, UUID4, field_serializer
from datetime import datetime
from typing import Optional


class MediaBase(BaseModel):
    media_type: str  # image, video


class MediaCreate(MediaBase):
    report_id: UUID4


class MediaUpdate(BaseModel):
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class MediaInDB(MediaBase):
    id: UUID4
    report_id: UUID4
    media_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class Media(MediaInDB):
    """
    Media response dengan URL yang bisa langsung dipakai
    URL akan di-generate otomatis saat serialization
    """
    url: Optional[str] = None
    
    @classmethod
    def from_orm_with_url(cls, db_media, url: str):
        """Helper untuk create instance dengan URL"""
        media = cls.model_validate(db_media)
        media.url = url
        return media