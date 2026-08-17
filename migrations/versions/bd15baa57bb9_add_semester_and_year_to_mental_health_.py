"""add semester and year to mental_health_records

Revision ID: bd15baa57bb9
Revises: da3eea3a1b55
Create Date: 2026-07-26 11:56:51.385141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd15baa57bb9'
down_revision: Union[str, Sequence[str], None] = 'da3eea3a1b55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Added nullable first since the table already has rows; a follow-up
    # migration tightens both to NOT NULL once existing rows are backfilled.
    op.add_column('mental_health_records', sa.Column('semester', sa.Integer(), nullable=True))
    op.add_column('mental_health_records', sa.Column('year', sa.Integer(), nullable=True))
    op.create_check_constraint(
        'ck_mental_health_records_semester_digit', 'mental_health_records', 'semester >= 0 AND semester <= 9'
    )
    op.create_check_constraint(
        'ck_mental_health_records_year_4digit', 'mental_health_records', 'year >= 1000 AND year <= 9999'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_mental_health_records_year_4digit', 'mental_health_records', type_='check')
    op.drop_constraint('ck_mental_health_records_semester_digit', 'mental_health_records', type_='check')
    op.drop_column('mental_health_records', 'year')
    op.drop_column('mental_health_records', 'semester')
