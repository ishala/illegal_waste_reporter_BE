from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from app.dependencies import get_db, Hasher
from app.crud import crud_user
from app.schemas.user import User, UserCreate
from app.core.config import settings
from app.core.security import create_access_token
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
    
    access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": exist_user.email, "user_id": str(exist_user.id), "role": exist_user.role},
        expires_delta=access_token_expires
    )
    
    return APIResponse(
        success=True,
        message=SuccessMessage.LOGIN_SUCCESS,
        data={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )