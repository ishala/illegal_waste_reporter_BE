from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4

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

from app.crud.crud_media import minio_service

router = APIRouter()

@router.get("/", response_model=List[Report])
def read_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    """
    Ambil semua reports
    """
    if valid_user is not None:
        reports = crud_report.get_reports(db=db, skip=skip, limit=limit)
        
        for report in reports:
            for media in report.media:
                media.url = minio_service.get_file_url(media.media_url, expires=7200)
        return reports
    else:
        return None

@router.get("/{report_id}", response_model=Report)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    print(db_report)
    check_resource_ownership(
        resource_user_id=db_report.user_id,
        current_user=current_user,
        resource_name="report"
    )

    for media in db_report.media:
            media.url = minio_service.get_file_url(media.media_url, expires=7200)
    return db_report

@router.post("/", response_model=Report, 
                status_code=status.HTTP_201_CREATED)
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
    # Ambil user id
    user_id = current_user.id

    # Buat dan Ambil location id
    location_data = LocationCreate(
        latitude=latitude,
        longitude=longitude,
        address=address
    )
    db_location = crud_location.create_location(db=db, location=location_data)

    # Cek atau ambil report status id
    status_id = None
    if report_status_id:
        try:
            status_id = UUID(report_status_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid report_status_id format"
            )
    else:
        status_id = crud_report_status.get_pending_status(db=db)

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
            crud_media.create_media(
                db=db,
                report_id=db_report.id,
                media_url=object_name,
                media_type=media_type
            )
    
    db.refresh(db_report)
    return db_report

@router.patch("/{report_id}", response_model=Report)
def update_report(
    report_id: UUID,
    report: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update report
    """
    new_location_id = None
    
    db_report = crud_report.get_report(db=db, report_id=report_id)
    if db_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
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
        new_location_id = db_location.id
    
    # Update report
    db_report = crud_report.update_report(
        db=db, 
        report_id=report_id, 
        report=report,
        new_location_id=new_location_id
    )
    
    if db_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return db_report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hapus report
    """
    db_report = crud_report.get_report(db=db, report_id=report_id)
    if db_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # ✅ Validasi ownership
    check_resource_ownership(
        resource_user_id=db_report.user_id,
        current_user=current_user,
        resource_name="report"
    )
    
    for media in db_report.media:
        minio_service.delete_file(media.url)

    success = crud_report.delete_report(db=db, report_id=report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )