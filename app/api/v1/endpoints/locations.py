from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4

from app.dependencies import get_db
from app.crud import crud_location
from app.schemas.location import (
    Location,
    LocationNearby,
    LocationCreate,
    LocationUpdate
)

router = APIRouter()

@router.get("/", response_model=List[Location])
def read_location(
    location_id = UUID,
    db: Session = Depends(get_db)
):
    """
    Ambil semua locations
    """
    location = crud_location.get_location(db=db, location_id=location_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location

@router.post("/", response_model=Location, 
                status_code=status.HTTP_201_CREATED)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db)
):
    db_location = crud_location.create_location(db=db, location=location)
    return db_location

@router.post("/nearby", response_model=List[Location])
def find_nearby_locations(
    search: LocationNearby,
    db: Session = Depends(get_db)
):
    locations = crud_location.get_nearby_locations(
        db=db,
        latitude=search.latitude,
        longitude=search.longitude,
        radius_km=search.radius_km
    )
    return locations

@router.put("/{location_id}", response_model=Location)
def update_location(
    location_id: UUID,
    location: LocationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update location
    """
    db_location = crud_location.update_location(
        db=db, location=location, location_id=location_id)
    if db_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return db_location

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Hapus location
    """
    success = crud_location.delete_location(
        db=db, location_id=location_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not founde"
        )