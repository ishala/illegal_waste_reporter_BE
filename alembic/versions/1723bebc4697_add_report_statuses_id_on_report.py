"""add_report_statuses_id_on_report

Revision ID: 1723bebc4697
Revises: 3a44ffba411a
Create Date: 2026-01-13 21:04:35.899440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '1723bebc4697'
down_revision: Union[str, None] = '3a44ffba411a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'reports',
        sa.Column('report_status_id', UUID(as_uuid=True), nullable=True)
    )

    op.create_foreign_key(
        'fk_reports_report_status_id',
        'reports',
        'report_statuses',
        ['report_status_id'],
        ['id']
    )

def downgrade() -> None:
    op.drop_constraint(
        'fk_reports_report_status_id',
        'reports',
        type_='foreignkey'
    )
    
    # Hapus kolom report_status_id
    op.drop_column('reports', 'report_status_id')
