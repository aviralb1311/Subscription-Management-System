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
    
    users_cols = {c['name'] for c in inspector.get_columns('users')}
    
    # Handle password column safely
    if 'hashed_password' in users_cols and 'password_hash' in users_cols:
        # Both exist - preserve hashed_password, drop password_hash if empty
        op.execute("UPDATE users SET hashed_password = COALESCE(hashed_password, password_hash) WHERE hashed_password IS NULL")
        op.drop_column('users', 'password_hash')
    elif 'password_hash' in users_cols and 'hashed_password' not in users_cols:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    elif 'hashed_password' not in users_cols and 'password_hash' not in users_cols:
        raise RuntimeError("Neither password_hash nor hashed_password exists on users table")
    
    # Handle name columns safely
    if 'full_name' not in users_cols:
        op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
        if 'first_name' in users_cols or 'last_name' in users_cols:
            op.execute("UPDATE users SET full_name = TRIM(CONCAT(COALESCE(first_name,''), CASE WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN ' ' ELSE '' END, COALESCE(last_name,''))) WHERE (first_name IS NOT NULL OR last_name IS NOT NULL)")
    
    # role_permissions table
    tables = set(inspector.get_table_names())
    if 'role_permissions' not in tables:
        if 'permissions' in tables and 'roles' in tables:
            op.create_table('role_permissions',
            sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='fk_role_permissions_permission_id_permissions'),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_role_permissions_role_id_roles'),
            sa.PrimaryKeyConstraint('role_id', 'permission_id', name='pk_role_permissions')
            )
    
    # roles.permissions
    roles_cols = {c['name'] for c in inspector.get_columns('roles')}
    if 'permissions' not in roles_cols:
        op.add_column('roles', sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    roles_cols = {c['name'] for c in inspector.get_columns('roles')}
    
    if 'permissions' in roles_cols:
        op.drop_column('roles', 'permissions')
    if 'role_permissions' in tables:
        op.drop_table('role_permissions')
