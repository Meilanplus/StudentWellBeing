"""set mental_health_records semester and year not null

Revision ID: 11686ef1e460
Revises: bd15baa57bb9
Create Date: 2026-07-26 11:59:14.686546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11686ef1e460'
down_revision: Union[str, Sequence[str], None] = 'bd15baa57bb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('mental_health_records', 'semester', nullable=False)
    op.alter_column('mental_health_records', 'year', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('mental_health_records', 'year', nullable=True)
    op.alter_column('mental_health_records', 'semester', nullable=True)
