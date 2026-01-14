from pydantic import BaseModel, UUID4, Field, field_validator, computed_field
from typing import Optional
from decimal import Decimal

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    address: Optional[str] = None
    city: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None

class LocationInDB(BaseModel):
    id: UUID4
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    
    class Config:
        from_attributes = True

class Location(LocationInDB):
    pass

class LocationNearby(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = Field(default=5.0, description="Search radius in kilometers")