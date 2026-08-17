"""create intervention_reports table

Revision ID: 911660139a2d
Revises: 0151ee840d91
Create Date: 2026-07-31 11:51:22.247270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '911660139a2d'
down_revision: Union[str, Sequence[str], None] = '0151ee840d91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'intervention_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('report_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_intervention_reports_id'), 'intervention_reports', ['id'], unique=False)
    op.create_index(op.f('ix_intervention_reports_created_at'), 'intervention_reports', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_intervention_reports_created_at'), table_name='intervention_reports')
    op.drop_index(op.f('ix_intervention_reports_id'), table_name='intervention_reports')
    op.drop_table('intervention_reports')
