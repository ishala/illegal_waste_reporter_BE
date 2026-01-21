from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies import get_db
from app.crud import (
    crud_verification, 
    crud_report_status,
    crud_report)
from app.schemas.user import User
from app.schemas.verification import (
    Verification,
    VerificationCreate,
)
from app.core.security import (
    get_current_active_admin
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
def read_verifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in as an admin"
        )
    db_verifications = crud_verification.get_verifications(
        db=db, skip=skip, limit=limit
    )
    if db_verifications is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Field \"verification\" not found"
        )
    verif_data = Verification.model_validate(db_verifications)
    return APIResponse(
        success=True,
        message=SuccessMessage.VERIFICATION_RETRIEVED,
        data=verif_data.model_dump()
    )

@router.get("/{verification_id}", response_model=APIResponse,
            status_code=HTTPStatus.OK)
def read_verification(
    verification_id: UUID,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in as an admin"
        )
    
    db_verification = crud_verification.get_verification(
        db=db, verification_id=verification_id
    )
    if db_verification is None:
        error = ErrorMessage.REPORT_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="Field \"verification\" not found"
        )
    verif_data = Verification.model_validate(db_verification)
    return APIResponse(
        success=True,
        message=SuccessMessage.VERIFICATION_RETRIEVED,
        data=verif_data.model_dump()
    )

@router.post("/", response_model=APIResponse,
             status_code=HTTPStatus.CREATED)
def create_verification(
    verification: VerificationCreate,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin),
):
    if valid_user is None:
        error = ErrorMessage.UNAUTHORIZED
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in as an admin"
        )
    
    report_status = verification.report_status
    
    db_verification = crud_verification.create_verification(
        db=db,
        verification=verification,
        report_id=verification.report_id,
        admin_id=valid_user.id
    )
    
    if db_verification is not None and report_status != "Pending":
        try:
            new_report_status_id = crud_report_status.get_status_id_by_name(
                db=db, name=report_status)

            db_report = crud_report.get_report(
                db=db, report_id=verification.report_id)

            if db_report is None:
                error = ErrorMessage.REPORT_NOT_FOUND
                ErrorMessage.raise_exception(
                    error_type=error,
                )

            db_report.report_status_id = new_report_status_id

            db_report = crud_report.update_report(
                db=db,
                report_id=verification.report_id,
                report=db_report
            )
        except ValueError as e:
            error = ErrorMessage.REPORT_NOT_FOUND
            ErrorMessage.raise_exception(
                error_type=error,
            )
    else:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
        )
    verif_data = Verification.model_validate(db_verification)

    return APIResponse(
        success=True,
        message=SuccessMessage.VERIFICATION_CREATED,
        data=verif_data.model_dump()
    )

@router.delete("/{verification_id}", 
               status_code=HTTPStatus.NO_CONTENT)
def delete_verification(
    verification_id: UUID,
    db: Session = Depends(get_db),
    valid_user: Session = Depends(get_current_active_admin)
):
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please make sure you are logged in as an admin"
        )

    success = crud_verification.delete_verification(
        db=db, verification_id=verification_id
    )
    if not success:
        error = ErrorMessage.VALIDATION_ERROR
        ErrorMessage.raise_exception(
            error_type=error,
            details="Failed to delete at \"verification\""
        )
    else:
        APIResponse(
            success=True,
            message=SuccessMessage.VERIFICATION_DELETED,
        )