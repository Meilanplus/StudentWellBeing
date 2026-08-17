"""rename attendance_records status to att_per

Revision ID: 221c05889cc7
Revises: 9065440f0eb4
Create Date: 2026-07-25 19:01:59.973022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '221c05889cc7'
down_revision: Union[str, Sequence[str], None] = '9065440f0eb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('attendance_records', 'status', new_column_name='att_per')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('attendance_records', 'att_per', new_column_name='status')
