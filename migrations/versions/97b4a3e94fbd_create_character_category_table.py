"""create character_category table

Revision ID: 97b4a3e94fbd
Revises: 11686ef1e460
Create Date: 2026-07-27 16:05:53.696969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97b4a3e94fbd'
down_revision: Union[str, Sequence[str], None] = '11686ef1e460'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'character_category',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('sub_category', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('category_id'),
    )
    op.create_index(op.f('ix_character_category_category_id'), 'character_category', ['category_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_character_category_category_id'), table_name='character_category')
    op.drop_table('character_category')
