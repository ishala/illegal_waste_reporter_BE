from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate

def create_session(db: Session, 
                   session: SessionCreate) -> SessionModel:
    """Buat session baru"""
    db_session = SessionModel(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session_by_refresh_token(db: Session, refresh_token: str) -> Optional[SessionModel]:
    """Get session by refresh token"""
    return db.query(SessionModel).filter(
        SessionModel.refresh_token == refresh_token
    ).first()

def get_active_session_by_refresh_token(db: Session, refresh_token: str) -> Optional[SessionModel]:
    """Get active & non-expired session by refresh token"""
    now = datetime.utcnow()
    return db.query(SessionModel).filter(
        and_(
            SessionModel.refresh_token == refresh_token,
            SessionModel.is_active == True,
            SessionModel.expires_at > now,
            SessionModel.revoked_at.is_(None)
        )
    ).first()

def get_user_sessions(db: Session, user_id: UUID, active_only: bool = True) -> List[SessionModel]:
    """Get all sessions for a user"""
    query = db.query(SessionModel).filter(SessionModel.user_id == user_id)
    
    if active_only:
        now = datetime.utcnow()
        query = query.filter(
            and_(
                SessionModel.is_active == True,
                SessionModel.expires_at > now,
                SessionModel.revoked_at.is_(None)
            )
        )
    
    return query.order_by(SessionModel.created_at.desc()).all()

def update_session(db: Session, session_id: UUID, session_update: SessionUpdate) -> Optional[SessionModel]:
    """Update session"""
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

def update_last_used(db: Session, session_id: UUID) -> Optional[SessionModel]:
    """Update last_used_at timestamp"""
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if db_session:
        db_session.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session

def revoke_session(db: Session, session_id: UUID) -> Optional[SessionModel]:
    """Revoke (logout) a specific session"""
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if db_session:
        db_session.is_active = False
        db_session.revoked_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session

def revoke_all_user_sessions(db: Session, user_id: UUID) -> int:
    """Revoke all sessions for a user (logout from all devices)"""
    now = datetime.utcnow()
    result = db.query(SessionModel).filter(
        and_(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        )
    ).update({
        "is_active": False,
        "revoked_at": now
    })
    db.commit()
    return result

def delete_expired_sessions(db: Session) -> int:
    """Delete all expired sessions (cleanup job)"""
    now = datetime.utcnow()
    result = db.query(SessionModel).filter(
        SessionModel.expires_at < now
    ).delete()
    db.commit()
    return result