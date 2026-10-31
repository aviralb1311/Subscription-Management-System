"""sync_auth_models

Revision ID: f1a2b3c4d5e6
Revises: 0018ca6cfb19
Create Date: 2026-10-31 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '0018ca6cfb19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Align users table with current models
    try:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    except Exception:
        pass
    try:
        op.drop_column('users', 'first_name')
    except Exception:
        pass
    try:
        op.drop_column('users', 'last_name')
    except Exception:
        pass
    try:
        op.drop_column('users', 'email_verified_at')
    except Exception:
        pass
    try:
        op.drop_column('users', 'last_login_at')
    except Exception:
        pass
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    
    # Add role_permissions if missing
    try:
        op.create_table('role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
        )
    except Exception:
        pass
    
    # Add permissions to roles if missing
    try:
        op.add_column('roles', sa.Column('permissions', sa.JSON(), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_column('roles', 'permissions')
    except Exception:
        pass
    try:
        op.drop_table('role_permissions')
    except Exception:
        pass
    try:
        op.drop_column('users', 'full_name')
    except Exception:
        pass
    try:
        op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    except Exception:
        pass
    try:
        op.alter_column('users', 'hashed_password', new_column_name='password_hash')
    except Exception:
        pass
