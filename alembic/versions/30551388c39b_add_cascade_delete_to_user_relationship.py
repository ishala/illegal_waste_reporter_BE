"""add cascade delete to user relationship

Revision ID: 30551388c39b
Revises: d6004c2d8359
Create Date: 2026-01-18 11:32:17.475005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30551388c39b'
down_revision: Union[str, None] = 'd6004c2d8359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
