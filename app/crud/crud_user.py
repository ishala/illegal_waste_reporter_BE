from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# READ
def get_user(
    db: Session,
    user_id: UUID
) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(
    db: Session,
    email: str
) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

## FOR ADMIN
def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# CREATE
def create_user(
    db: Session,
    user: UserCreate,
) -> User:
    # TODO: Hash password sebelum disimpan (gunakan passlib atau bcrypt)
    # hashed_password = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password, # Ganti dengan hashed_password nanti
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    user_id: UUID,
    user: UserUpdate
) -> Optional[User]:
    db_user = get_user(db=db, user_id=user_id)
    if db_user is None:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(
    db: Session,
    user_id: UUID
) -> bool:
    db_user = get_user(db=db, user_id=user_id)
    if db_user is None:
        return None
    
    db.delete(db_user)
    db.commit()
    return True