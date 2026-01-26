from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.core.config import settings
from app.crud import crud_user, crud_session
from app.dependencies import get_db
from app.schemas.user import TokenData, User
from app.schemas.session import SessionCreate

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
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def create_refresh_token() -> str:
    """Generate secure random refresh token"""
    return secrets.token_urlsafe(32)

def create_session(
    db: Session,
    user_id: UUID,
    device_name: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create new session and return refresh token"""
    refresh_token = create_refresh_token()
    
    if expires_delta:
        expires_at = datetime.utcnow() + expires_delta
    else:
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    session_data = SessionCreate(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        device_name=device_name
    )
    
    crud_session.create_session(db=db, session=session_data)
    return refresh_token

def verify_token(token: str, credentials_exception):
    # Verifikasi JWT Token dan extract payload
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
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

def check_resource_ownership(
    resource_user_id: UUID,
    current_user: User,
    resource_name: str = "resource"
) -> None:
    """
    Check apakah current_user adalah owner dari resource atau admin.
    Raise 403 jika bukan.
    
    Args:
        resource_user_id: user_id dari resource (report, etc)
        current_user: User yang sedang login
        resource_name: Nama resource untuk error message
    
    Raises:
        HTTPException 403 jika user bukan owner dan bukan admin
    """
    if current_user.role == "admin":
        return  # Admin bisa akses semua
    
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to access this {resource_name}"
        )

def is_owner_or_admin(
    resource_user_id: UUID,
    current_user: User
) -> bool:
    """
    Return True jika user adalah owner atau admin
    """
    return current_user.role == "admin" \
        or resource_user_id == current_user.id