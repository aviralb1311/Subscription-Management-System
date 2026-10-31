"""sync_auth_models

Revision ID: f1a2b3c4d5e6
Revises: 0018ca6cfb19
Create Date: 2026-10-31 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '0018ca6cfb19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    users_cols = {c['name']: c for c in inspector.get_columns('users')}
    has_password_hash = 'password_hash' in users_cols
    has_hashed_password = 'hashed_password' in users_cols
    
    # Handle password column safely
    if has_hashed_password and has_password_hash:
        # Check for conflicts
        result = bind.execute(text("SELECT COUNT(*) FROM users WHERE password_hash IS NOT NULL AND hashed_password IS NOT NULL AND password_hash != hashed_password"))
        conflicts = result.scalar()
        if conflicts and conflicts > 0:
            raise RuntimeError(f"Conflicting password values found in {conflicts} users. Manual resolution required.")
        # Preserve all hashes
        bind.execute(text("UPDATE users SET hashed_password = password_hash WHERE hashed_password IS NULL AND password_hash IS NOT NULL"))
        op.drop_column('users', 'password_hash')
    elif has_password_hash and not has_hashed_password:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    elif not has_hashed_password and not has_password_hash:
        raise RuntimeError("Neither password_hash nor hashed_password exists on users table. Cannot proceed safely.")
    
    # Re-inspect after potential changes
    users_cols = {c['name']: c for c in inspector.get_columns('users')}
    
    # Handle name columns safely - preserve all existing data
    if 'full_name' not in users_cols:
        op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
        has_first = 'first_name' in users_cols
        has_last = 'last_name' in users_cols
        if has_first and has_last:
            bind.execute(text("UPDATE users SET full_name = NULLIF(TRIM(CONCAT(COALESCE(first_name,''), ' ', COALESCE(last_name,''))), '') WHERE full_name IS NULL"))
        elif has_first and not has_last:
            bind.execute(text("UPDATE users SET full_name = first_name WHERE full_name IS NULL AND first_name IS NOT NULL"))
        elif has_last and not has_first:
            bind.execute(text("UPDATE users SET full_name = last_name WHERE full_name IS NULL AND last_name IS NOT NULL"))
    
    # role_permissions table with data preservation
    tables = set(inspector.get_table_names())
    if 'role_permissions' not in tables:
        if 'permissions' in tables and 'roles' in tables:
            perms_cols = {c['name'] for c in inspector.get_columns('permissions')}
            roles_cols_check = {c['name'] for c in inspector.get_columns('roles')}
            if 'id' in perms_cols and 'id' in roles_cols_check:
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
