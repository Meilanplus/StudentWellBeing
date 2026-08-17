"""create nichq_detail table

Revision ID: b388120deba1
Revises: 97b4a3e94fbd
Create Date: 2026-07-27 18:36:36.423110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b388120deba1'
down_revision: Union[str, Sequence[str], None] = '97b4a3e94fbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'nichq_detail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('inattentive', sa.Integer(), nullable=False),
        sa.Column('hyperactive', sa.Integer(), nullable=False),
        sa.Column('performance', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_nichq_detail_id'), 'nichq_detail', ['id'], unique=False)
    op.create_index(op.f('ix_nichq_detail_event_date'), 'nichq_detail', ['event_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_nichq_detail_event_date'), table_name='nichq_detail')
    op.drop_index(op.f('ix_nichq_detail_id'), table_name='nichq_detail')
    op.drop_table('nichq_detail')
