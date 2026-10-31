"""Add products and plans tables

Revision ID: cc4gd2ee91ge
Revises: bb3fc1dd80fd
Create Date: 2026-10-31 06:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cc4gd2ee91ge'
down_revision = 'bb3fc1dd80fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('products',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=100), nullable=True),
    sa.Column('product_type', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('cost_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('sales_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_code'), 'products', ['code'], unique=True)
    
    op.create_table('product_variants',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('sku', sa.String(length=100), nullable=True),
    sa.Column('attributes', sa.Text(), nullable=True),
    sa.Column('price_adjustment', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_variants_sku'), 'product_variants', ['sku'], unique=True)
    
    op.create_table('plans',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=100), nullable=True),
    sa.Column('billing_cycle', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('auto_close', sa.Boolean(), nullable=True),
    sa.Column('allow_pause_resume', sa.Boolean(), nullable=True),
    sa.Column('availability_start', sa.DateTime(), nullable=True),
    sa.Column('availability_end', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plans_code'), 'plans', ['code'], unique=True)
    
    op.create_table('plan_versions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('effective_from', sa.DateTime(), nullable=False),
    sa.Column('effective_to', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('plan_versions')
    op.drop_index(op.f('ix_plans_code'), table_name='plans')
    op.drop_table('plans')
    op.drop_index(op.f('ix_product_variants_sku'), table_name='product_variants')
    op.drop_table('product_variants')
    op.drop_index(op.f('ix_products_code'), table_name='products')
    op.drop_table('products')
