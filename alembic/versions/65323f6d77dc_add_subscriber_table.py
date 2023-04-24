"""add subscriber table

Revision ID: 65323f6d77dc
Revises: e043bd09b84b
Create Date: 2023-04-24 22:25:18.720707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65323f6d77dc'
down_revision = 'e043bd09b84b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscriber',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriber')
    # ### end Alembic commands ###
