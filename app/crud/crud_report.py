from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate
from app.crud import crud_location

# READ
def get_report(db: Session, 
                      report_id: UUID) -> Optional[Report]:
    # Ambil 1 report berdasarkan ID
    return db.query(Report).filter(Report.id == report_id).first()

def get_reports(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Report]:
    # Ambil all reports dengan pagination
    return db.query(Report).offset(skip).limit(limit).all()

# CREATE
def create_report(
    db: Session,
    report: ReportCreate,
    user_id: UUID,
    location_id: UUID
) -> Report:
    # Buat satu report baru
    db_report = Report(
        user_id=user_id,
        location_id=location_id,
        category=report.category,
        description=report.description,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return db_report

# UPDATE
def update_report(
    db: Session,
    report_id: UUID,
    report: ReportUpdate,
    new_location_id: Optional[UUID] = None
) -> Optional[Report]:
    """
    Update report
    """
    db_report = get_report(db, report_id)
    if db_report is None:
        return None
    
    # Update hanya field yang diisi
    if report.category is not None:
        db_report.category = report.category
    if report.description is not None:
        db_report.description = report.description
    if new_location_id is not None:
        db_report.location_id = new_location_id

    db.commit()
    db.refresh(db_report)
    return db_report

# DELETE
def delete_report(db: Session, report_id: UUID) -> bool:
    """
    Hapus report
    Return True jika berhasil, False jika tidak ditemukan
    """
    db_report = get_report(db, report_id)
    if db_report is None:
        return False
    
    db.delete(db_report)
    db.commit()
    return True