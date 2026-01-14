from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from geoalchemy2.shape import to_shape
import uuid

from app.db.session import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coordinates = Column(
        Geometry(geometry_type='POINT', srid=4326),
        nullable=False
    )
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    __table_args__ = (
        Index('idx_location_coordinates', 'coordinates', postgresql_using='gist'),
    )
    
    reports = relationship("Report", back_populates="location")
    
    @property
    def latitude(self) -> float:
        """Extract latitude dari coordinates"""
        if self.coordinates is not None:
            point = to_shape(self.coordinates)
            return point.y
        return 0.0
    
    @property
    def longitude(self) -> float:
        """Extract longitude dari coordinates"""
        if self.coordinates is not None:
            point = to_shape(self.coordinates)
            return point.x
        return 0.0