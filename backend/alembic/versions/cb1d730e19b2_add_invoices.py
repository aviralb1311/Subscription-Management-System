"""add_invoices

Revision ID: cb1d730e19b2
Revises: de4dd343c8d5
Create Date: 2026-10-31 08:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cb1d730e19b2'
down_revision = 'de4dd343c8d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('invoices',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_number', sa.String(length=50), nullable=False),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('issue_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('billing_period_start', sa.DateTime(), nullable=True),
    sa.Column('billing_period_end', sa.DateTime(), nullable=True),
    sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('discount_total', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('total', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_number')
    )
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)
    
    op.create_table('invoice_lines',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('tax_rate', sa.Numeric(precision=5, scale=4), nullable=True),
    sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('line_subtotal', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('line_total', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('price_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('invoice_lines')
    op.drop_index(op.f('ix_invoices_invoice_number'), table_name='invoices')
    op.drop_table('invoices')
