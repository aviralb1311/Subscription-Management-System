"""sync_products_variants

Revision ID: e7f8g9h0i1j2
Revises: f1a2b3c4d5e6
Create Date: 2026-10-31 10:06:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e7f8g9h0i1j2'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        op.add_column('product_variants', sa.Column('price_adjustment', sa.Numeric(15, 2), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('product_variants', sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'))
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_column('product_variants', 'currency')
    except Exception:
        pass
    try:
        op.drop_column('product_variants', 'price_adjustment')
    except Exception:
        pass
