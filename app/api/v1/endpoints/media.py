from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies import get_db
from app.crud import crud_media, crud_report
from app.schemas.user import User
from app.core.security import get_current_user, check_resource_ownership
from app.crud.crud_media import minio_service
from app.models.media import Media

from app.api.status_code import (
    APIResponse,
    SuccessMessage,
    ErrorMessage,
    HTTPStatus
)

router = APIRouter()

@router.post('/{report_id}/media',
             response_model=APIResponse,
             status_code=HTTPStatus.CREATED)
async def upload_report_media(
    report_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        error = ErrorMessage.UNAUTHORIZED
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in"
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
        resource_name='report'
    )

    uploaded_media = []
    for file in files:
        if file.filename == '':
            continue
        
        obj_name, media_type = minio_service.upload_file(
            file=file,
            folder=f'report_media/{report_id}'
        )
        
        db_media = crud_media.create_media(
            db=db,
            report_id=report_id,
            media_url=obj_name,
            media_type=media_type
        )
        if db_media is None:
            error = ErrorMessage.MEDIA_UPLOAD_FAILED
            ErrorMessage.raise_exception(
                error_type=error,
            )

        uploaded_media.append({
            "id": str(db_media.id),
            "media_type": db_media.media_type,
            "created_at": db_media.created_at
        })

    return APIResponse(
        success=True,
        message=SuccessMessage.MEDIA_UPLOADED,
        data=uploaded_media
    )

@router.get("/{report_id}/media/{media_id}/url", status_code=HTTPStatus.OK,
            response_model=APIResponse)
def get_media_url(
    report_id: UUID,
    media_id: UUID,
    expires: int = 100,
    db: Session = Depends(get_db),
    current_user: Session = Depends(get_current_user)
):
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

    db_media = db.query(Media).filter(
        Media.id == media_id,
        Media.report_id == report_id
    ).first()

    if db_media is None:
        error = ErrorMessage.MEDIA_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )
    
    url = minio_service.get_file_url(
        obj_name=db_media.media_url,
        expires=expires
    )

    return_data = {
        "media_id": str(media_id),
        "media_type": db_media.media_type,
        "url": url,
        "expires_in": expires
    }

    return APIResponse(
        success=True,
        data=return_data
    )

@router.delete("/{report_id}/media/{media_id}", 
               status_code=HTTPStatus.NO_CONTENT)
def delete_report_media(
    report_id: UUID,
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    db_media = db.query(Media).filter(
        Media.id == media_id,
        Media.report_id == report_id
    ).first()
    if db_media is None:
        error = ErrorMessage.MEDIA_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    success = crud_media.delete_media(db=db, media_id=media_id)

    if not success:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
            details="Failed to delete at \"media\""
        )
    else:
        APIResponse(
            success=True,
            message=SuccessMessage.MEDIA_DELETED,
        )