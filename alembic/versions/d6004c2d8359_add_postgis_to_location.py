"""add_postgis_to_location

Revision ID: d6004c2d8359
Revises: 1723bebc4697
Create Date: 2026-01-14 21:34:50.318468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = 'd6004c2d8359'
down_revision: Union[str, None] = '1723bebc4697'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Add coordinates column
    op.add_column(
        'locations',
        sa.Column('coordinates', Geometry(geometry_type='POINT', srid=4326), nullable=True)
    )
    
    # Migrate existing data: convert lat/lon to POINT
    op.execute("""
        UPDATE locations 
        SET coordinates = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    # Make coordinates NOT NULL after migration
    op.alter_column('locations', 'coordinates', nullable=False)
    
    # Create spatial index
    op.execute("""
        CREATE INDEX idx_location_coordinates 
        ON locations USING GIST (coordinates)
    """)
    
    # Drop old columns
    op.drop_column('locations', 'latitude')
    op.drop_column('locations', 'longitude')


def downgrade() -> None:
    # Add back lat/lon columns
    op.add_column('locations', sa.Column('latitude', sa.Numeric(precision=10, scale=8)))
    op.add_column('locations', sa.Column('longitude', sa.Numeric(precision=11, scale=8)))
    
    # Extract lat/lon from coordinates
    op.execute("""
        UPDATE locations 
        SET latitude = ST_Y(coordinates),
            longitude = ST_X(coordinates)
    """)
    
    # Drop index and column
    op.execute('DROP INDEX IF EXISTS idx_location_coordinates')
    op.drop_column('locations', 'coordinates')
