from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.verification import Verification
from app.schemas.verification import VerificationCreate, VerificationUpdate

# READ
def get_verification(
    db: Session,
    verification_id: UUID
) -> Optional[Verification]:
    return db.query(Verification).filter(Verification.id == verification_id).first()

def get_verifications(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Verification]:
    return db.query(Verification).offset(skip).limit(limit).all()

# CREATE
def create_verification(
    db: Session,
    verification: VerificationCreate,
    report_id: UUID,
    admin_id: UUID
) -> Verification:
    db_verification = Verification(
        admin_id=admin_id,
        report_id=report_id,
        notes=verification.notes
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)

    return db_verification

# UPDATE
def update_verification(
    db: Session,
    verification_id: UUID,
    verification: VerificationUpdate,
) -> Optional[Verification]:
    db_verification = get_verification(db=db, 
                                       verification_id=verification_id)
    if db_verification is None:
        return None
    
    if verification.notes is not None:
        db_verification.notes = verification.notes
    
    db.commit()
    db.refresh(db_verification)
    return db_verification

# DELETE
def delete_verification(
    db: Session,
    verification_id: UUID
) -> bool:
    db_verification = get_verification(db, verification_id)
    if db_verification is None:
        return False
    
    db.delete(db_verification)
    db.commit()
    return True