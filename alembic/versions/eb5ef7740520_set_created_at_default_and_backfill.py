"""set created_at default and backfill

Revision ID: eb5ef7740520
Revises: 880a92665fe3
Create Date: 2025-07-24 22:38:43.082434

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb5ef7740520"
down_revision = "880a92665fe3"
branch_labels = None
depends_on = None


def upgrade():
    # set default NOW() and fill existing NULL values
    op.execute("ALTER TABLE scraped_items ALTER COLUMN created_at SET DEFAULT NOW();")
    op.execute("UPDATE scraped_items SET created_at = NOW() WHERE created_at IS NULL;")


def downgrade():
    # undo the default (cannot easily undo the backfill)
    op.execute("ALTER TABLE scraped_items ALTER COLUMN created_at DROP DEFAULT;")
