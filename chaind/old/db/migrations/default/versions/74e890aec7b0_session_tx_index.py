"""Session tx index

Revision ID: 74e890aec7b0
Revises: 7ac591b16c68
Create Date: 2021-08-26 10:51:53.651692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74e890aec7b0'
down_revision = '7ac591b16c68'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
            'session',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('otx_id', sa.Integer, sa.ForeignKey('otx.id'), nullable=False),
            sa.Column('session', sa.String(256), nullable=False),
    )
    op.create_index('idx_session', 'session', ['session', 'otx_id'], unique=True)


def downgrade():
    op.drop_index('idx_session')
    op.drop_table('session')
