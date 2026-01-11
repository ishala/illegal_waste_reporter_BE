from sqlalchemy import Column, String, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    latitude = Column(Numeric(precision=10, scale=8), nullable=False)
    longitude = Column(Numeric(precision=11, scale=8), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    
    reports = relationship("Report", back_populates="location")