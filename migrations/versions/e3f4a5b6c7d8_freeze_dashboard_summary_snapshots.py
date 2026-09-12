"""freeze dashboard summary snapshots (kpis/class_breakdown/student_cases)

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4a5b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('dashboard_summaries', sa.Column('school_kpis', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('dashboard_summaries', sa.Column('class_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('dashboard_summaries', sa.Column('student_cases', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('dashboard_summaries', 'student_cases')
    op.drop_column('dashboard_summaries', 'class_breakdown')
    op.drop_column('dashboard_summaries', 'school_kpis')
