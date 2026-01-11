from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional, List

from app.schemas.location import Location, LocationCreate, LocationUpdate
from app.schemas.media import Media
from app.schemas.user import UserInDB


class ReportBase(BaseModel):
    category: str
    description: Optional[str] = None


class ReportCreate(ReportBase):
    location: LocationCreate = None


class ReportUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[LocationUpdate] = None


class ReportInDB(ReportBase):
    id: UUID4
    user_id: UUID4
    location_id: UUID4
    # status_id removed
    created_at: datetime

    class Config:
        from_attributes = True


class Report(ReportInDB):
    location: Optional[Location] = None
    media: List[Media] = Field(default_factory=list)

# Admin
class ReportWithUser(Report):
    user: Optional[UserInDB] = None