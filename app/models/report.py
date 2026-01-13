from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    report_status_id = Column(UUID(as_uuid=True), ForeignKey("report_statuses.id"), nullable=False)
    category = Column(String, nullable=False)
    # Contoh: plastic, organic, electronic, construction, hazardous
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")
    location = relationship("Location", back_populates="reports")
    report_status = relationship("ReportStatus", back_populates="reports")
    verifications = relationship("Verification", back_populates="report")
    media = relationship("Media", back_populates="report", cascade="all, delete-orphan")