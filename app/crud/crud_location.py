from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate

# READ
def get_location(db: Session,
                 location_id: UUID) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()

def get_locations(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Location]:
    return db.query(Location).offset(skip).limit(limit).all()

# CREATE
def create_location(
    db: Session,
    location: LocationCreate,
) -> Location:
    db_location = Location(
        latitude = location.latitude,
        longitude = location.longitude,
        address = location.address,
        city = location.city
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# UPDATE
def update_location(
    db: Session,
    location_id: UUID,
    location: LocationUpdate
) -> Optional[Location]:
    """
    Update location
    """
    db_location = get_location(db=db, location_id=location_id)
    if db_location is None:
        return None
    
    if location.latitude is not None:
        db_location.latitude = location.latitude
    if location.longitude is not None:
        db_location.longitude = location.longitude
    if location.address is not None:
        db_location.address = location.address
    if location.city is not None:
        db_location.city = location.city
    
    db.commit()
    db.refresh(db_location)
    return db_location

# DELETE
def delete_location(
    db: Session, location_id: UUID
    ) -> bool:
    """Hapus location"""
    db_location = get_location(db=db, location_id=location_id)
    if db_location is None:
        return False
    db.delete(db_location)
    db.commit()
    return True