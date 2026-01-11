from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


class VerificationBase(BaseModel):
    notes: Optional[str] = None


class VerificationCreate(VerificationBase):
    report_id: UUID4


class VerificationUpdate(BaseModel):
    notes: Optional[str] = None


class VerificationInDB(VerificationBase):
    id: UUID4
    report_id: UUID4
    admin_id: UUID4
    verified_at: datetime

    class Config:
        from_attributes = True


class Verification(VerificationInDB):
    pass