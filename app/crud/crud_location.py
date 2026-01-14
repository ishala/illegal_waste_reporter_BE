from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint
from geoalchemy2.elements import WKTElement

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

def get_nearby_locations(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    limit: int = 100
) -> List[Location]:
    """
    Cari lokasi dalam radius tertentu (kilometer)
    Menggunakan PostGIS spatial query
    """
    # Create point from lat/lon
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    # Query dengan ST_DWithin untuk radius search (lebih cepat karena pakai index)
    # Convert km to degrees (approximation: 1 degree ≈ 111 km)
    radius_degrees = radius_km / 111.0
    locations = db.query(Location).filter(
        func.ST_DWithin(Location.coordinates, point, radius_degrees)
    ).limit(limit).all()

    return locations

def get_location_with_distance(
    db: Session,
    location_id: UUID,
    from_latitude: float,
    from_longitude: float
):
    """
    Ambil location dengan jarak dari titik tertentu
    """
    point = func.ST_SetSRID(func.ST_MakePoint(from_longitude, from_latitude), 4326)
    
    location = db.query(
        Location,
        func.ST_Distance(
            Location.coordinates,
            point,
            True  # Use spheroid for accurate distance
        ).label('distance_meters')
    ).filter(Location.id == location_id).first()
    
    return location

# CREATE
def create_location(
    db: Session,
    location: LocationCreate,
) -> Location:
    point = f'POINT({location.longitude} {location.latitude})'
    db_location = Location(
        coordinates=point,
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
    
    if location.latitude is not None and location.longitude is not None:
        point = f'POINT({location.longitude} {location.latitude})'
        db_location.coordinates = point
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