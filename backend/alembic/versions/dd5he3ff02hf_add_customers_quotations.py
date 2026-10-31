"""Add customers and quotations tables

Revision ID: dd5he3ff02hf
Revises: cc4gd2ee91ge
Create Date: 2026-10-31 07:12:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dd5he3ff02hf'
down_revision = 'cc4gd2ee91ge'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('customers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('billing_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('shipping_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('tax_id', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    
    op.create_table('quotations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('quotation_number', sa.String(length=50), nullable=False),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('valid_until', sa.DateTime(), nullable=True),
    sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('discount_total', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('tax_total', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('converted_to_subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('quotation_number')
    )
    op.create_index(op.f('ix_quotations_quotation_number'), 'quotations', ['quotation_number'], unique=True)
    
    op.create_table('quotation_lines',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('product_variant_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_version_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ),
    sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('quotation_lines')
    op.drop_index(op.f('ix_quotations_quotation_number'), table_name='quotations')
    op.drop_table('quotations')
    op.drop_table('customers')
