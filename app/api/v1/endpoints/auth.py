from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from app.dependencies import get_db, Hasher
from app.crud import crud_user
from app.schemas.user import User, UserCreate, Token, TokenData
from app.core.config import settings
from app.core.security import create_access_token, get_current_user

router = APIRouter()
hasher = Hasher()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    exist_user = crud_user.get_user_by_email(db=db, email=user.email)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email are registered"
        )
    
    hash_pw = hasher.get_password_hash(user.password)
    user.password = hash_pw
    
    db_user = crud_user.create_user(db=db, user=user)
    return db_user

@router.post("/login", response_model=Token)
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    verified_pw = hasher.verify_password(form_data.password, exist_user.password)
    
    if not exist_user or not verified_pw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": exist_user.email, "user_id": str(exist_user.id), "role": exist_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }