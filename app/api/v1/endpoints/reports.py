from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.dependencies import get_db
from app.crud import (
    crud_report, 
    crud_location, 
    crud_report_status,
    crud_media)
from app.schemas.report import (
    Report,
    ReportCreate,
    ReportUpdate
)
from app.schemas.location import LocationCreate
from app.schemas.user import User
from app.core.security import (
    get_current_user,
    get_current_active_admin,
    check_resource_ownership
)
from app.api.status_code import (
    APIResponse,
    SuccessMessage,
    ErrorMessage,
    HTTPStatus
)

from app.crud.crud_media import minio_service

router = APIRouter()

@router.get("/", response_model=APIResponse,
            status_code=HTTPStatus.OK)
def read_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    """
    Ambil semua reports
    """
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )
    reports = crud_report.get_reports(db=db, skip=skip, limit=limit)

    if reports is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    for report in reports:
        for media in report.media:
            media.url = minio_service.get_file_url(media.media_url, expires=7200)
    reports_data = [Report.model_validate(report).model_dump()
                    for report in reports]
    
    return APIResponse(
        success=True,
        message=SuccessMessage.REPORT_RETRIEVED,
        data={
            "reports": reports_data,
            "total": len(reports_data)
        }
    )

@router.get("/{report_id}", response_model=Report,
            status_code=HTTPStatus.OK)
def read_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ambil 1 report berdasarkan ID
    """
    db_report = crud_report.get_report(db=db, report_id=report_id)
    if db_report is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    valid_owner = check_resource_ownership(
        resource_user_id=db_report.user_id,
        current_user=current_user,
        resource_name="report"
    )
    
    if valid_owner is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have access permission"
        )

    for media in db_report.media:
            media.url = minio_service.get_file_url(media.media_url, expires=7200)

    report_data = Report.model_validate(db_report)
    return APIResponse(
        success=True,
        message=SuccessMessage.REPORT_RETRIEVED,
        data=report_data.model_dump()
    )

@router.post("/", response_model=APIResponse,
                status_code=HTTPStatus.CREATED)
async def create_report(
    category: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    report_status_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Buat report baru
    """
    if current_user is None:
        error = ErrorMessage.UNAUTHORIZED
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in"
        )
    # Ambil user id
    user_id = current_user.id

    # Buat dan Ambil location id
    location_data = LocationCreate(
        latitude=latitude,
        longitude=longitude,
        address=address
    )
    db_location = crud_location.create_location(db=db, location=location_data)

    if db_location is None:
        error = ErrorMessage.MISSING_REQUIRED_FIELD
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure those \"location\" fields are completed"
        )

    # Cek atau ambil report status id
    status_id = None
    if report_status_id:
        try:
            status_id = UUID(report_status_id)
        except ValueError:
            error = ErrorMessage.MISSING_REQUIRED_FIELD
            ErrorMessage.raise_exception(
                error_type=error,
                details="Please make sure those \"status id\" fields are completed"
            )
    else:
        status_id = crud_report_status.get_status_id_by_name(db=db)

    # Buat report
    report_data = ReportCreate(
        category=category,
        description=description,
        location=location_data,
        report_status_id=status_id
    )

    db_report = crud_report.create_report(
        db=db,
        report=report_data,
        user_id=user_id,
        location_id=db_location.id,
        report_status_id=status_id
    )

    if db_report is None:
        error = ErrorMessage.REPORT_CREATION_FAILED
        ErrorMessage.raise_exception(
            error_type=error,
        )

    if files:
        for file in files:
            # Skip jika file kosong
            if file.filename == '':
                continue
            # Upload ke MinIO
            object_name, media_type = minio_service.upload_file(
                file=file,
                folder=f"report_media/{db_report.id}"
            )

            # Simpan metadata ke database
            try:
                db_media = crud_media.create_media(
                    db=db,
                    report_id=db_report.id,
                    media_url=object_name,
                    media_type=media_type
                )
            except ValueError as e:
                error = ErrorMessage.MEDIA_UPLOAD_FAILED
                ErrorMessage.raise_exception(
                    error_type=error,
                )

    db.refresh(db_report)
    report_data = Report.model_validate(db_report)
    return APIResponse(
        success=True,
        message=SuccessMessage.REPORT_CREATED,
        data=report_data.model_dump()
    )

@router.patch("/{report_id}", response_model=APIResponse,
              status_code=HTTPStatus.OK)
def update_report(
    report_id: UUID,
    report: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update report
    """
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
        )
    new_location_id = None

    db_report = crud_report.get_report(db=db, report_id=report_id)
    if db_report is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    check_resource_ownership(
        resource_user_id=db_report.user_id,
        current_user=current_user,
        resource_name="report"
    )

    # Jika ada update location, buat location BARU
    if report.location is not None:
        db_location = crud_location.create_location(
            db=db,
            location=report.location
        )
        if db_location is None:
            error = ErrorMessage.INVALID_FORMAT
            ErrorMessage.raise_exception(
                error_type=error,
                details="Please make sure those \"create location\" fields are completed"
            )
        new_location_id = db_location.id

    # Update report
    db_report = crud_report.update_report(
        db=db, 
        report_id=report_id, 
        report=report,
        new_location_id=new_location_id
    )

    if db_report is None:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure those \"report\" fields are completed"
        )
    
    report_data = Report.model_validate(db_report)
    return APIResponse(
        success=True,
        message=SuccessMessage.REPORT_UPDATED,
        data=report_data
    )

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hapus report
    """
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
        )
    db_report = crud_report.get_report(db=db, report_id=report_id)
    if db_report is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    check_resource_ownership(
        resource_user_id=db_report.user_id,
        current_user=current_user,
        resource_name="report"
    )
    
    for media in db_report.media:
        if media:
            minio_service.delete_file(media.url)

    success = crud_report.delete_report(db=db, report_id=report_id)
    if not success:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Failed to delete at \"report\""
        )
    else:
        APIResponse(
            success=True,
            message=SuccessMessage.REPORT_DELETED,
        )