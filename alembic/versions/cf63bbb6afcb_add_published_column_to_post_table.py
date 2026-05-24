"""add published column to post table

Revision ID: cf63bbb6afcb
Revises: b9aefb68d01e
Create Date: 2026-05-24 11:18:30.237373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa 


# revision identifiers, used by Alembic.
revision: str = 'cf63bbb6afcb'
down_revision: Union[str, Sequence[str], None] = 'b9aefb68d01e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'posts',
        sa.Column('published', sa.Boolean(), nullable=False, server_default='TRUE')
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'published')
    pass
