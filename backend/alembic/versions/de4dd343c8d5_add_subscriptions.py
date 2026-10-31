"""add_subscriptions

Revision ID: de4dd343c8d5
Revises: a7021373f625
Create Date: 2026-10-31 08:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'de4dd343c8d5'
down_revision = 'a7021373f625'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('subscriptions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subscription_number', sa.String(length=50), nullable=True),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_version_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('next_billing_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('paused_at', sa.DateTime(), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(), nullable=True),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('renewal_date', sa.DateTime(), nullable=True),
    sa.Column('price_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subscription_number')
    )
    op.create_index(op.f('ix_subscriptions_subscription_number'), 'subscriptions', ['subscription_number'], unique=True)
    
    op.create_table('subscription_lines',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('plan_version_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('line_total', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('price_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('subscription_lines')
    op.drop_index(op.f('ix_subscriptions_subscription_number'), table_name='subscriptions')
    op.drop_table('subscriptions')
