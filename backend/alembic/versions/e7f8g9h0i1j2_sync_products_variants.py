"""sync_products_variants

Revision ID: e7f8g9h0i1j2
Revises: f1a2b3c4d5e6
Create Date: 2026-10-31 10:06:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'e7f8g9h0i1j2'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # product_variants
    var_cols = {c['name'] for c in inspector.get_columns('product_variants')}
    if 'price_adjustment' not in var_cols:
        op.add_column('product_variants', sa.Column('price_adjustment', sa.Numeric(15, 2), nullable=True))
    if 'currency' not in var_cols:
        op.add_column('product_variants', sa.Column('currency', sa.String(length=3), nullable=True))
        op.execute("UPDATE product_variants SET currency = 'USD' WHERE currency IS NULL")
    
    # products
    prod_cols = {c['name'] for c in inspector.get_columns('products')}
    if 'price_adjustment' not in prod_cols:
        op.add_column('products', sa.Column('price_adjustment', sa.Numeric(15, 2), nullable=True))
    if 'currency' not in prod_cols:
        op.add_column('products', sa.Column('currency', sa.String(length=3), nullable=True))
        op.execute("UPDATE products SET currency = 'USD' WHERE currency IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    var_cols = {c['name'] for c in inspector.get_columns('product_variants')}
    if 'currency' in var_cols:
        op.drop_column('product_variants', 'currency')
    if 'price_adjustment' in var_cols:
        op.drop_column('product_variants', 'price_adjustment')
    prod_cols = {c['name'] for c in inspector.get_columns('products')}
    if 'currency' in prod_cols:
        op.drop_column('products', 'currency')
    if 'price_adjustment' in prod_cols:
        op.drop_column('products', 'price_adjustment')
