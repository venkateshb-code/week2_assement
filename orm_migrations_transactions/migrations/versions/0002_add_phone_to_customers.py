"""add phone to customers

Revision ID: 0002_add_phone
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_phone"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("customers", sa.Column("phone", sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column("customers", "phone")
