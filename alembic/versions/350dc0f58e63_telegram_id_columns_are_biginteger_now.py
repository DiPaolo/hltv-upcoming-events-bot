"""telegram_id columns are BigInteger now

Revision ID: 350dc0f58e63
Revises: 372f964eb1ad
Create Date: 2023-05-01 20:43:14.657037

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '350dc0f58e63'
down_revision = '372f964eb1ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('chat', 'telegram_id', type_=sa.BIGINT, existing_type=sa.INTEGER)
    op.alter_column('user', 'telegram_id', type_=sa.BIGINT, existing_type=sa.INTEGER)


def downgrade() -> None:
    op.alter_column('chat', 'telegram_id', type_=sa.INTEGER, existing_type=sa.BIGINT)
    op.alter_column('user', 'telegram_id', type_=sa.INTEGER, existing_type=sa.BIGINT)
