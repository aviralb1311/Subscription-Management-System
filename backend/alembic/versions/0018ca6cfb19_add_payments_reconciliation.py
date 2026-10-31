"""add_payments_reconciliation

Revision ID: 0018ca6cfb19
Revises: cb1d730e19b2
Create Date: 2026-10-31 08:49:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0018ca6cfb19'
down_revision = 'cb1d730e19b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('payments',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('payment_number', sa.String(length=50), nullable=True),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('payment_date', sa.DateTime(), nullable=True),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('external_reference', sa.String(length=100), nullable=True),
    sa.Column('idempotency_key', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('unallocated_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('payment_number'),
    sa.UniqueConstraint('idempotency_key')
    )
    op.create_index(op.f('ix_payments_payment_number'), 'payments', ['payment_number'], unique=True)
    
    op.create_table('payment_allocations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('allocated_amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('allocated_at', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('credit_notes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('credit_note_number', sa.String(length=50), nullable=True),
    sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('credit_note_number')
    )
    op.create_index(op.f('ix_credit_notes_credit_note_number'), 'credit_notes', ['credit_note_number'], unique=True)
    
    op.create_table('refunds',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('refund_number', sa.String(length=50), nullable=True),
    sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('credit_note_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('refund_date', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['credit_note_id'], ['credit_notes.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refund_number')
    )
    op.create_index(op.f('ix_refunds_refund_number'), 'refunds', ['refund_number'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_refunds_refund_number'), table_name='refunds')
    op.drop_table('refunds')
    op.drop_index(op.f('ix_credit_notes_credit_note_number'), table_name='credit_notes')
    op.drop_table('credit_notes')
    op.drop_table('payment_allocations')
    op.drop_index(op.f('ix_payments_payment_number'), table_name='payments')
    op.drop_table('payments')
