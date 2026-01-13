"""add_report_statuses_table

Revision ID: 3a44ffba411a
Revises: 4bb6e17da635
Create Date: 2026-01-13 20:33:02.377267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '3a44ffba411a'
down_revision: Union[str, None] = '4bb6e17da635'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'report_statuses',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False)
    )
    report_status = table('report_statuses',
        column('name', sa.String)
    )
    
    # INSERT data baru
    op.bulk_insert(report_status, [
        {'name': 'Pending'},
        {'name': 'Verified'},
        {'name': 'Rejected'},
    ])


def downgrade() -> None:
    op.drop_table('report_statuses')