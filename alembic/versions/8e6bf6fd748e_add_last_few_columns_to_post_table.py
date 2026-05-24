"""add last few columns to post table

Revision ID: 8e6bf6fd748e
Revises: 0aa0b94886fd
Create Date: 2026-05-24 12:58:31.191034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e6bf6fd748e'
down_revision: Union[str, Sequence[str], None] = '0aa0b94886fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'posts', 
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
     )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'created_at') 
    pass
