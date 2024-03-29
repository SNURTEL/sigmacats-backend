"""allow_to_retire_bike

Revision ID: 47d563d762de
Revises: db70b95f5994
Create Date: 2023-12-09 21:25:38.661234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '47d563d762de'
down_revision: Union[str, None] = 'db70b95f5994'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bike', sa.Column('is_retired', sa.Boolean(), nullable=False, server_default='0'))
    op.alter_column('bike', 'is_retired', server_default=None)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bike', 'is_retired')
    # ### end Alembic commands ###
