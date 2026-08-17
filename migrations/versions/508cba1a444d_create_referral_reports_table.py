"""create referral_reports table

Revision ID: 508cba1a444d
Revises: 911660139a2d
Create Date: 2026-07-31 13:08:06.517768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '508cba1a444d'
down_revision: Union[str, Sequence[str], None] = '911660139a2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'referral_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('referral_type', sa.String(length=50), nullable=False),
        sa.Column('referral_to', sa.String(length=100), nullable=False),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('report_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_referral_reports_id'), 'referral_reports', ['id'], unique=False)
    op.create_index(op.f('ix_referral_reports_created_at'), 'referral_reports', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_referral_reports_created_at'), table_name='referral_reports')
    op.drop_index(op.f('ix_referral_reports_id'), table_name='referral_reports')
    op.drop_table('referral_reports')
