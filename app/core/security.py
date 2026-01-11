from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_user
from app.dependencies import get_db
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    # JWT Access Token
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    # Verifikasi JWT Token dan extract payload
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, user_id=user_id, role=role)
        return token_data
    except JWTError:
        raise credentials_exception

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Dependency untuk mendapatkan user yg sedang login
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credential validation are failed",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token_data = verify_token(token, credentials_exception)
    user = crud_user.get_user_by_email(db=db, email=token_data.email)
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_admin(
    current_user = Depends(get_current_user)
):
    # Dependency untuk memastikan user adalah admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesnt have admin access"
        )
    return current_user