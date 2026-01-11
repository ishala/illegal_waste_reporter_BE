from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4

from app.dependencies import get_db
from app.crud import crud_report, crud_location
from app.schemas.report import (
    Report,
    ReportCreate,
    ReportUpdate
)
from app.schemas.location import (
    LocationCreate,
    LocationUpdate
)

router = APIRouter()

@router.get("/", response_model=List[Report])
def read_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Ambil semua reports
    """
    reports = crud_report.get_reports(db=db, skip=skip, limit=limit)
    return reports

@router.get("/{report_id}", response_model=Report)
def read_report(
    report_id: UUID,
    db: Session = Depends(get_db)
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
    return db_report

@router.post("/", response_model=Report, 
                status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db)
):
    """
    Buat report baru
    """
    # 1. Buat location dulu via CRUD
    db_location = crud_location.create_location(
        db=db,
        location=report.location
    )
    
    # 2. Untuk sementara, buat dummy user_id (nanti ganti dengan auth)
    # TODO: Ganti dengan user_id dari JWT token
    dummy_user_id = uuid4()  # Temporary solution
    
    # 3. Buat report
    db_report = crud_report.create_report(
        db=db,
        report=report,
        user_id=dummy_user_id,
        location_id=db_location.id,
    )
    
    return db_report

@router.put("/{report_id}", response_model=Report)
def update_report(
    report_id: UUID,
    report: ReportUpdate,
    db: Session = Depends(get_db)
):
    """
    Update report
    """
    db_report = crud_report.update_report(db=db, report_id=report_id, report=report)
    if db_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return db_report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Hapus report
    """
    success = crud_report.delete_report(db=db, report_id=report_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )