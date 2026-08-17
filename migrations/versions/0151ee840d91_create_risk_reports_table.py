"""create risk_reports table

Revision ID: 0151ee840d91
Revises: b388120deba1
Create Date: 2026-07-31 09:18:14.070817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0151ee840d91'
down_revision: Union[str, Sequence[str], None] = 'b388120deba1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'risk_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('report_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_risk_reports_id'), 'risk_reports', ['id'], unique=False)
    op.create_index(op.f('ix_risk_reports_created_at'), 'risk_reports', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_risk_reports_created_at'), table_name='risk_reports')
    op.drop_index(op.f('ix_risk_reports_id'), table_name='risk_reports')
    op.drop_table('risk_reports')
