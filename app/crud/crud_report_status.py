from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.report_status import ReportStatus
from app.schemas.report_status import ReportStatusCreate, ReportStatusUpdate

# READ
def get_report_status(db: Session,
                      report_status_id: UUID) -> Optional[ReportStatus]:
    return db.query(ReportStatus).filter(ReportStatus.id == report_status_id).first()

def get_report_statuses(db: Session) -> List[ReportStatus]:
    return db.query(ReportStatus).all()

def get_status_id_by_name(db: Session, name: str = 'Pending'):
    return db.query(ReportStatus).filter(ReportStatus.name == name).first().id

# CREATE
def create_report_status(
    db: Session,
    report_status: ReportStatusCreate,
) -> ReportStatus:
    db_repstatus = ReportStatus(
        name=report_status.name
    )
    db.add(db_repstatus)
    db.commit()
    db.refresh(db_repstatus)
    return db_repstatus

# UPDATE
def update_report_status(
    db: Session,
    report_status: ReportStatusUpdate,
    report_status_id: UUID
) -> Optional[ReportStatus]:
    db_repstatus = get_report_status(db, report_status_id)
    if db_repstatus is None:
        return None
    
    if report_status.name is not None:
        db_repstatus.name = report_status.name
    
    db.commit()
    db.refresh(db_repstatus)
    return db_repstatus

# DELETE
def delete_report_status(
    db: Session,
    report_status_id: UUID
) -> bool:
    db_repstatus = get_report_status(db, report_status_id)
    if db_repstatus is None:
        return False
    db.delete(db_repstatus)
    db.commit()
    return True