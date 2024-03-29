"""translation table is many-to-many for matches and streamers

Revision ID: f9c7f0878276
Revises: 65323f6d77dc
Create Date: 2023-04-26 08:43:41.838073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9c7f0878276'
down_revision = '65323f6d77dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('translation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('streamer_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.ForeignKeyConstraint(['streamer_id'], ['streamer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('streamer_match_id_fkey', 'streamer', type_='foreignkey')
    op.drop_column('streamer', 'match_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('streamer', sa.Column('match_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('streamer_match_id_fkey', 'streamer', 'match', ['match_id'], ['id'])
    op.drop_table('translation')
    # ### end Alembic commands ###
