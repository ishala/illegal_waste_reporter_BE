from pydantic import BaseModel, UUID4
from typing import Optional
from decimal import Decimal

class LocationBase(BaseModel):
    latitude: Decimal
    longitude: Decimal
    address: Optional[str] = None
    city: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    address: Optional[str] = None
    city: Optional[str] = None

class LocationInDB(LocationBase):
    id: UUID4
    
    class Config:
        from_attributes = True

class Location(LocationInDB):
    pass