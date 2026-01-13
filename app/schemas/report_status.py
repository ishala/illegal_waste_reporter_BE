from pydantic import BaseModel, UUID4
from typing import Optional

class ReportStatusBase(BaseModel):
    name: str

class ReportStatusCreate(ReportStatusBase):
    pass

class ReportStatusUpdate(ReportStatusCreate):
    name: Optional[str] = None

class ReportStatusInDB(BaseModel):
    id: UUID4
    name: str

    class Config:
        from_attributes = True

class ReportStatus(ReportStatusInDB):
    pass