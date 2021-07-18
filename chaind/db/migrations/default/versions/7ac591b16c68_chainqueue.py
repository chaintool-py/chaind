"""chainqueue

Revision ID: 7ac591b16c68
Revises: b139fca16787
Create Date: 2021-06-03 13:11:24.579148

"""
from alembic import op
import sqlalchemy as sa

from chainqueue.db.migrations.default.export import (
    chainqueue_upgrade,
    chainqueue_downgrade,
    )

# revision identifiers, used by Alembic.
revision = '7ac591b16c68'
down_revision = 'b139fca16787'
branch_labels = None
depends_on = None


def upgrade():
    chainqueue_upgrade()


def downgrade():
    chainqueue_downgrade()
