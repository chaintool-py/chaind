"""chainsyncer

Revision ID: b139fca16787
Revises: 
Create Date: 2021-06-03 13:09:23.731381

"""
from alembic import op
import sqlalchemy as sa

from chainsyncer.db.migrations.default.export import (
        chainsyncer_upgrade,
        chainsyncer_downgrade,
        )

# revision identifiers, used by Alembic.
revision = 'b139fca16787'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    chainsyncer_upgrade()


def downgrade():
    chainsyncer_downgrade()
