"""Adjust account model

Revision ID: 58b91be3d785
Revises: 47d563d762de
Create Date: 2023-12-20 15:36:41.519327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '58b91be3d785'
down_revision: Union[str, None] = '47d563d762de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('account', 'password_hash')
    for column in (sa.Column("hashed_password", sa.String(length=72), nullable=False),
                   sa.Column("is_active", sa.Boolean, default=True, nullable=False),
                   sa.Column("is_superuser", sa.Boolean, default=False, nullable=False),
                   sa.Column("is_verified", sa.Boolean, default=False, nullable=False),):
        op.add_column('account', column)


def downgrade() -> None:
    for column_name in ('hashed_password', 'is_active', 'is_superuser', 'is_verified'):
        op.drop_column('account', column_name)
    op.add_column('account', sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False))
