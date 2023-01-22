"""initial

Revision ID: bd51f5fc9fd4
Revises: 
Create Date: 2023-01-22 13:26:10.495950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd51f5fc9fd4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unix_time_utc_sec', sa.BigInteger(), nullable=False),
    sa.Column('team1_id', sa.Integer(), nullable=True),
    sa.Column('team2_id', sa.Integer(), nullable=True),
    sa.Column('stars', sa.Enum('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', name='matchstars'), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['team1_id'], ['team.id'], ),
    sa.ForeignKeyConstraint(['team2_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    op.drop_table('team')
    # ### end Alembic commands ###
