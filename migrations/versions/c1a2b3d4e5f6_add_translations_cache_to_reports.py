"""add translations cache to risk/intervention/referral reports

Revision ID: c1a2b3d4e5f6
Revises: 508cba1a444d
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '508cba1a444d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = ('risk_reports', 'intervention_reports', 'referral_reports')


def upgrade() -> None:
    """Upgrade schema."""
    # Caches each report's on-demand translation per language code (e.g.
    # {"en": {...}, "zh": {...}}) so viewing a saved report in a non-canonical
    # language only pays the translation cost once, not on every view.
    for table in TABLES:
        op.add_column(
            table,
            sa.Column('translations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table in TABLES:
        op.drop_column(table, 'translations')
