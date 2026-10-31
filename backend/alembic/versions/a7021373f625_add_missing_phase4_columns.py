"""add_missing_phase4_columns

Revision ID: a7021373f625
Revises: dd5he3ff02hf
Create Date: 2026-10-31 08:04:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a7021373f625'
down_revision = 'dd5he3ff02hf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Align with model design
    op.add_column('quotations', sa.Column('approved_by', sa.String(length=255), nullable=True))
    op.add_column('quotations', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('quotations', sa.Column('rejected_by', sa.String(length=255), nullable=True))
    op.add_column('quotations', sa.Column('rejected_at', sa.DateTime(), nullable=True))
    op.add_column('quotations', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('quotations', sa.Column('terms_conditions', sa.Text(), nullable=True))
    op.add_column('quotation_lines', sa.Column('currency', sa.String(length=3), nullable=True))
    op.add_column('quotation_lines', sa.Column('price_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # Fix types to match models
    op.alter_column('quotation_lines', 'description', type_=sa.Text(), existing_type=sa.String(length=255), existing_nullable=True)
    op.alter_column('quotation_lines', 'quantity', type_=sa.Integer(), existing_type=sa.Numeric(precision=10, scale=3), existing_nullable=False, postgresql_using='quantity::integer')
    op.alter_column('quotations', 'created_by', type_=sa.String(length=255), existing_type=postgresql.UUID(as_uuid=True), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('quotations', 'created_by', type_=postgresql.UUID(as_uuid=True), existing_type=sa.String(length=255), existing_nullable=True)
    op.alter_column('quotation_lines', 'quantity', type_=sa.Numeric(precision=10, scale=3), existing_type=sa.Integer(), existing_nullable=False)
    op.alter_column('quotation_lines', 'description', type_=sa.String(length=255), existing_type=sa.Text(), existing_nullable=True)
    op.drop_column('quotation_lines', 'price_snapshot')
    op.drop_column('quotation_lines', 'currency')
    op.drop_column('quotations', 'terms_conditions')
    op.drop_column('quotations', 'rejection_reason')
    op.drop_column('quotations', 'rejected_at')
    op.drop_column('quotations', 'rejected_by')
    op.drop_column('quotations', 'approved_at')
    op.drop_column('quotations', 'approved_by')
