"""create mental_health_records table

Revision ID: da3eea3a1b55
Revises: 221c05889cc7
Create Date: 2026-07-26 11:37:42.315094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da3eea3a1b55'
down_revision: Union[str, Sequence[str], None] = '221c05889cc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'mental_health_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('whooley', sa.String(length=10), nullable=False),
        sa.Column('gad2_score', sa.Integer(), nullable=False),
        sa.Column('gad2_status', sa.String(length=10), nullable=False),
        sa.CheckConstraint('gad2_score >= 0 AND gad2_score <= 9', name='ck_mental_health_records_gad2_score_digit'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_mental_health_records_id'), 'mental_health_records', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_mental_health_records_id'), table_name='mental_health_records')
    op.drop_table('mental_health_records')
