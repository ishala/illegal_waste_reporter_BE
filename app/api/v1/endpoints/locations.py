from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.security import get_current_user

from app.dependencies import get_db
from app.crud import crud_location
from app.schemas.user import User
from app.schemas.location import (
    Location,
    LocationNearby,
    LocationCreate,
    LocationUpdate
)
from app.api.status_code import (
    APIResponse,
    SuccessMessage,
    ErrorMessage,
    HTTPStatus
)

router = APIRouter()

@router.get("/", response_model=APIResponse,
            status_code=HTTPStatus.OK)
def read_location(
    location_id = UUID,
    db: Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    """
    Ambil semua locations
    """
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
        )
    db_location = crud_location.get_location(db=db, location_id=location_id)
    if db_location is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Field \"location\" not found"
        )
    location_data = Location.model_validate(db_location)
    return APIResponse(
        success=True,
        message=SuccessMessage.LOCATION_RETRIEVED,
        data=location_data.model_dump()
    )

@router.post("/", response_model=APIResponse,
                status_code=HTTPStatus.CREATED)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        error = ErrorMessage.UNAUTHORIZED
        ErrorMessage.raise_exception(
            error_type=error,
        )
    db_location = crud_location.create_location(db=db, location=location)
    if db_location is None:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
            details="Any field inside \"location\" are invalid"
        )

    location_data = Location.model_validate(db_location)
    return APIResponse(
        success=True,
        message=SuccessMessage.LOCATION_CREATED,
        data=location_data.model_dump()
    )

@router.post("/nearby", response_model=APIResponse,
             status_code=HTTPStatus.CREATED)
def find_nearby_locations(
    search: LocationNearby,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        error = ErrorMessage.UNAUTHORIZED
        ErrorMessage.raise_exception(
            error_type=error,
        )
    db_locations = crud_location.get_nearby_locations(
        db=db,
        latitude=search.latitude,
        longitude=search.longitude,
        radius_km=search.radius_km
    )
    if db_locations is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Field \"location\" not found"
        )

    locations_data = [Location.model_validate(loc).model_dump()
                      for loc in db_locations]
    return APIResponse(
        success=True,
        message=SuccessMessage.LOCATION_RETRIEVED,
        data={
            "locations": locations_data,
            "total": len(locations_data)
        }
    )

@router.put("/{location_id}", response_model=APIResponse,
            status_code=HTTPStatus.CREATED)
def update_location(
    location_id: UUID,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update location
    """
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
        )
    db_location = crud_location.update_location(
        db=db, location=location, location_id=location_id)
    if db_location is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Field \"location\" not found"
        )
    
    location_data = Location.model_validate(db_location)
    return APIResponse(
        success=True,
        message=SuccessMessage.LOCATION_UPDATED,
        data=location_data.model_dump()
    )

@router.delete("/{location_id}", 
               status_code=HTTPStatus.NO_CONTENT)
def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hapus location
    """
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
        )

    success = crud_location.delete_location(
        db=db, location_id=location_id)
    if not success:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
            details="Failed to delete at \"location\""
        )
    else:
        APIResponse(
            success=True,
            message=SuccessMessage.LOCATION_DELETED,
        )