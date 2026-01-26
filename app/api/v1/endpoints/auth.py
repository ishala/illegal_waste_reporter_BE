from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from app.dependencies import get_db, Hasher
from app.crud import crud_user, crud_session
from app.schemas.user import User, UserCreate
from app.schemas.session import Session as SessionSchema
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_session,
    get_current_user)
from app.api.status_code import (
    APIResponse, 
    SuccessMessage, 
    ErrorMessage,
    HTTPStatus
) 

router = APIRouter()
hasher = Hasher()

@router.post("/register", 
             response_model=APIResponse, 
             status_code=HTTPStatus.CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    exist_user = crud_user.get_user_by_email(db=db, email=user.email)
    if exist_user:
        error = ErrorMessage.EMAIL_EXISTS
        ErrorMessage.raise_exception(
            error_type=error,
            details="Please insert the correct registered account"
        )
    
    hash_pw = hasher.get_password_hash(user.password)
    user.password = hash_pw
    
    db_user = crud_user.create_user(db=db, user=user)
    if db_user is None:
        error = ErrorMessage.USER_CREATION_FAILED
        ErrorMessage.raise_exception(
            error_type=error
        )
    user_data = User.model_validate(db_user)

    return APIResponse(
        success=True,
        message=SuccessMessage.USER_REGISTERED,
        data=user_data.model_dump()
    )

@router.post("/login", 
             response_model=APIResponse,
             status_code=HTTPStatus.OK)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user dengan email dan password
    OAuth2PasswordRequestForm menggunakan 'username' field, 
    tapi kita pakai untuk email
    """
    exist_user = crud_user.get_user_by_email(db=db, email=form_data.username)
    if not exist_user:
        error = ErrorMessage.INVALID_CREDENTIALS
        ErrorMessage.raise_exception(
            error_type=error
        )
    verified_pw = hasher.verify_password(form_data.password, exist_user.password)
    if not verified_pw:
        error = ErrorMessage.INVALID_CREDENTIALS
        ErrorMessage.raise_exception(
            error_type=error
        )

    # Create Access Token
    access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": exist_user.email, "user_id": str(exist_user.id), "role": exist_user.role},
        expires_delta=access_token_expires
    )
    
    # Create Session with Refresh Token
    device_name = request.headers.get("User-Agent", "Unknown Device")
    refresh_token = create_session(
        db=db,
        user_id=exist_user.id,
        device_name=device_name
    )
    
    return APIResponse(
        success=True,
        message=SuccessMessage.LOGIN_SUCCESS,
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )

@router.post("/refresh",
             response_model=APIResponse,
             status_code=HTTPStatus.OK)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    # Get Session
    session = crud_session.get_active_session_by_refresh_token(
        db=db, refresh_token=refresh_token)
    if not session:
        error = ErrorMessage.INVALID_CREDENTIALS
        ErrorMessage.raise_exception(
            error_type=error,
            details="Invalid or expired refresh token"
        )
    
    # Get User
    user = crud_user.get_user_by_email(db=db, email=session.user.email)
    if not user:
        error = ErrorMessage.USER_NOT_FOUND
        ErrorMessage.raise_exception(
            error_type=error,
        )

    # Update last_used_at
    crud_session.update_last_used(db=db, session_id=session.id)
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )

@router.post("/logout",
             response_model=APIResponse,
             status_code=HTTPStatus.OK)
def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from current device
    """
    session = crud_session.get_session_by_refresh_token(db=db, refresh_token=refresh_token)
    
    if not session or session.user_id != current_user.id:
        error = ErrorMessage.INVALID_CREDENTIALS
        ErrorMessage.raise_exception(
            error_type=error,
            details="User not found"
        )
    
    crud_session.revoke_session(db=db, session_id=session.id)
    
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data=None
    )

@router.post("/logout-all",
             response_model=APIResponse,
             status_code=HTTPStatus.OK)
def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices
    """
    count = crud_session.revoke_all_user_sessions(db=db, user_id=current_user.id)
    
    return APIResponse(
        success=True,
        message=f"Logged out from {count} device(s)",
        data={"sessions_revoked": count}
    )

@router.get("/sessions",
            response_model=APIResponse,
            status_code=HTTPStatus.OK)
def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions for current user
    """
    sessions = crud_session.get_user_sessions(db=db, user_id=current_user.id, active_only=True)
    sessions_data = [SessionSchema.model_validate(s) for s in sessions]
    
    return APIResponse(
        success=True,
        message="Sessions retrieved successfully",
        data=[s.model_dump() for s in sessions_data]
    )