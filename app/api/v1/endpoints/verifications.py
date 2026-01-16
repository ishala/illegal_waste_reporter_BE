from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4

from app.dependencies import get_db
from app.crud import (
    crud_verification, 
    crud_report_status,
    crud_report)
from app.schemas.user import User
from app.schemas.verification import (
    Verification,
    VerificationCreate,
    VerificationUpdate
)
from app.core.security import (
    check_resource_ownership,
    get_current_active_admin
)

router = APIRouter()

@router.get("/", response_model=List[Verification])
def read_verifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    if valid_user is not None:
        verifications = crud_verification.get_verifications(
            db=db, skip=skip, limit=limit
        )
        return verifications
    else:
        return None

@router.get("/{verification_id}", response_model=Verification)
def read_verification(
    verification_id: UUID,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    if valid_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not allowed to access"
        )
    
    db_verification = crud_verification.get_verification(
        db=db, verification_id=verification_id
    )
    if db_verification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )
    return db_verification

@router.post("/", response_model=Verification,
             status_code=status.HTTP_201_CREATED)
def create_verification(
    verification: VerificationCreate,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin),
):
    if valid_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not allowed to access"
        )
    
    report_status = verification.report_status
    
    db_verification = crud_verification.create_verification(
        db=db,
        verification=verification,
        report_id=verification.report_id,
        admin_id=valid_user.id
    )
    
    if db_verification is not None and report_status != "Pending":
        new_report_status_id = crud_report_status.get_status_id_by_name(
            db=db, name=report_status)

        db_report = crud_report.get_report(
            db=db, report_id=verification.report_id)

        if db_report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        db_report.report_status_id = new_report_status_id

        db_report = crud_report.update_report(
            db=db,
            report_id=verification.report_id,
            report=db_report
        )
    return db_verification

@router.delete("/{verification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_verification(
    verification_id: UUID,
    db: Session = Depends(get_db),
    valid_user: Session = Depends(get_current_active_admin)
):
    if valid_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not allowed to access"
        )

    success = crud_verification.delete_verification(
        db=db, verification_id=verification_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification not found"
        )