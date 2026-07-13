"""add account_type enum constraint

Revision ID: 8f028c343fce
Revises: 10b0f9ce6c8e
Create Date: 2026-07-13 13:49:11.000737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f028c343fce'
down_revision: Union[str, Sequence[str], None] = '10b0f9ce6c8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    account_type_enum = sa.Enum('checking', 'savings', 'credit', 'investment', name='accounttype')
    account_type_enum.create(op.get_bind())
    op.alter_column(
        'accounts', 'account_type',
        type_=account_type_enum,
        existing_type=sa.String(),
        existing_nullable=False,
        postgresql_using='account_type::accounttype'
    )


def downgrade() -> None:
    op.alter_column(
        'accounts', 'account_type',
        type_=sa.String(),
        existing_type=sa.Enum('checking', 'savings', 'credit', 'investment', name='accounttype'),
        existing_nullable=False
    )
    sa.Enum(name='accounttype').drop(op.get_bind())
