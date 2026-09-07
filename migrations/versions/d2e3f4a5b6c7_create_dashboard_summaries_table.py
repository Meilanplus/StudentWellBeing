"""create dashboard_summaries table

Revision ID: d2e3f4a5b6c7
Revises: c1a2b3d4e5f6
Create Date: 2026-09-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'dashboard_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('translations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period'),
    )
    op.create_index(op.f('ix_dashboard_summaries_id'), 'dashboard_summaries', ['id'], unique=False)
    op.create_index(op.f('ix_dashboard_summaries_period'), 'dashboard_summaries', ['period'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_dashboard_summaries_period'), table_name='dashboard_summaries')
    op.drop_index(op.f('ix_dashboard_summaries_id'), table_name='dashboard_summaries')
    op.drop_table('dashboard_summaries')
