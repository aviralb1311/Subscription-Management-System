"""sync_auth_models

Revision ID: f1a2b3c4d5e6
Revises: 0018ca6cfb19
Create Date: 2026-10-31 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '0018ca6cfb19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Preserve existing data when aligning users table
    columns = {c['name'] for c in inspector.get_columns('users')}
    
    if 'password_hash' in columns and 'hashed_password' not in columns:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    elif 'hashed_password' not in columns:
        op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
        op.execute('UPDATE users SET hashed_password = password_hash WHERE password_hash IS NOT NULL')
        op.alter_column('users', 'hashed_password', nullable=False)
    
    # Add full_name from first_name/last_name if missing, preserving data
    if 'full_name' not in columns:
        op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
        op.execute("UPDATE users SET full_name = TRIM(CONCAT(COALESCE(first_name,''), ' ', COALESCE(last_name,''))) WHERE full_name IS NULL")
    
    # role_permissions table
    tables = set(inspector.get_table_names())
    if 'role_permissions' not in tables and 'permissions' in tables and 'roles' in tables:
        op.create_table('role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
        )
    
    # roles.permissions
    role_cols = {c['name'] for c in inspector.get_columns('roles')}
    if 'permissions' not in role_cols:
        op.add_column('roles', sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    role_cols = {c['name'] for c in inspector.get_columns('roles')}
    
    if 'permissions' in role_cols:
        op.drop_column('roles', 'permissions')
    if 'role_permissions' in tables:
        op.drop_table('role_permissions')
