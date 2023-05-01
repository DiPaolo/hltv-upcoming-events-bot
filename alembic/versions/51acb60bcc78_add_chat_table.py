"""add chat table

Revision ID: 51acb60bcc78
Revises: f9c7f0878276
Create Date: 2023-04-30 10:16:00.123406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51acb60bcc78'
down_revision = 'f9c7f0878276'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.add_column('user_request', sa.Column('chat_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_request', 'chat', ['chat_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_request', type_='foreignkey')
    op.drop_column('user_request', 'chat_id')
    op.drop_table('chat')
    # ### end Alembic commands ###