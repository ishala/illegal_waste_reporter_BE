from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


class Media(Base):
    __tablename__ = "medias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)  # image, video
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="media")