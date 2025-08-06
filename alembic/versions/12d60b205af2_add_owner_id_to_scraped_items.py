"""add owner_id to scraped_items

Revision ID: 12d60b205af2
Revises: e7a52672dd64
Create Date: 2025-08-06 22:59:02.421693

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Sequence, Union


revision: str = "12d60b205af2"
down_revision: Union[str, Sequence[str], None] = "e7a52672dd64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "scraped_items",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute("TRUNCATE TABLE scraped_items")

    op.create_foreign_key(
        "fk_scraped_items_owner", "scraped_items", "users", ["owner_id"], ["id"]
    )
    op.create_unique_constraint("uq_owner_url", "scraped_items", ["owner_id", "url"])
    op.alter_column("scraped_items", "owner_id", nullable=False)


def downgrade():
    op.drop_constraint("uq_owner_url", "scraped_items", type_="unique")
    op.drop_constraint("fk_scraped_items_owner", "scraped_items", type_="foreignkey")
    op.drop_column("scraped_items", "owner_id")
