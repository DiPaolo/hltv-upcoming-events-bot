"""add tournament

Revision ID: 41e3f5165eab
Revises: 3e91e0383e4f
Create Date: 2023-01-29 15:40:08.091245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41e3f5165eab'
down_revision = '3e91e0383e4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tournament',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('hltv_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hltv_id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('url')
    )
    op.add_column('match', sa.Column('tournament_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'match', 'tournament', ['tournament_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.drop_column('match', 'tournament_id')
    op.drop_table('tournament')
    # ### end Alembic commands ###
