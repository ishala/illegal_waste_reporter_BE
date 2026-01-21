from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies import get_db, Hasher
from app.crud import crud_user
from app.schemas.user import (
    User,
    UserUpdate
)
from app.core.security import (
    get_current_active_admin, 
    get_current_user,
    check_resource_ownership
)

from app.api.status_code import (
    APIResponse,
    SuccessMessage,
    ErrorMessage,
    HTTPStatus
)

router = APIRouter()
hasher = Hasher()

@router.get("/", response_model=APIResponse, 
            status_code=HTTPStatus.OK)
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    """
    Ambil semua users (API untuk Admin)
    """
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )

    users = crud_user.get_users(db=db, skip=skip, limit=limit)
    users_data = [User.model_validate(user).model_dump() 
                  for user in users]

    return APIResponse(
        success=True,
        message=SuccessMessage.USER_RETRIEVED,
        data={
            "users": users_data,
            "total": len(users_data)
        }
    )

@router.get("/me", response_model=APIResponse, 
            status_code=HTTPStatus.OK)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )

    user_data = User.model_validate(current_user)
    return APIResponse(
        success=True,
        message=SuccessMessage.USER_RETRIEVED,
        data=user_data.model_dump()
    )

@router.get("/{user_id}", response_model=APIResponse,
            status_code=HTTPStatus.OK)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    valid_user: User = Depends(get_current_active_admin)
):
    if valid_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )

    db_user = crud_user.get_user(db=db, user_id=user_id)
    if db_user is None:
        error = ErrorMessage.USER_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="User not found"
        )

    user_data = User.model_validate(db_user)
    return APIResponse(
        success=True,
        message=SuccessMessage.USER_RETRIEVED,
        data=user_data.model_dump()
    )

@router.put("/{user_id}", response_model=APIResponse,
            status_code=HTTPStatus.CREATED)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_owner = check_resource_ownership(
        resource_user_id=user_id,
        current_user=current_user,
        resource_name="user"
    )
    if is_owner is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )

    if user.email:
        exist_user = crud_user.get_user_by_email(db=db, email=user.email)
        if exist_user and exist_user.id != user_id:
            error = ErrorMessage.EMAIL_EXISTS
            ErrorMessage.raise_exception(
                error_type=error,
                details="Please insert the correct registered account"
            )
    if user.password:
        user.password = hasher.get_password_hash(user.password)

    db_user = crud_user.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        error = ErrorMessage.USER_CREATION_FAILED
        ErrorMessage.raise_exception(
            error_type=error,
            details=""
        )

    user_data = User.model_validate(db_user)
    return APIResponse(
        success=True,
        message=SuccessMessage.USER_RETRIEVED,
        data=user_data.model_dump()
    )

@router.delete("/{user_id}", 
               status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    if current_user is None:
        error = ErrorMessage.FORBIDDEN
        ErrorMessage.raise_exception(
            error_type=error,
            details="Make sure your account have permission"
        )
    success = crud_user.delete_user(db=db, user_id=user_id)
    if not success:
        error = ErrorMessage.USER_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
            details="User not found"
        )
    else:
        APIResponse(
            success=True,
            message=SuccessMessage.USER_DELETED,
            data={"user_id": str(user_id)}
        )