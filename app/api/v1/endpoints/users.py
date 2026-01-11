from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies import get_db, Hasher
from app.crud import crud_user
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate
)
from app.core.security import get_current_active_admin, get_current_user

router = APIRouter()
hasher = Hasher()

@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Ambil semua users (API untuk Admin)
    """
    users = crud_user.get_users(db=db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=User)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_user = crud_user.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # User hanya bisa update dirinya sendiri, kecuali admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tidak memiliki akses"
        )

    if user.email:
        exist_user = crud_user.get_user_by_email(db=db, email=user.email)
        if exist_user and exist_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan user lain"
            )
    if user.password:
        user.password = hasher.get_password_hash(user.password)
    
    db_user = crud_user.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Hapus user"""
    success = crud_user.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None