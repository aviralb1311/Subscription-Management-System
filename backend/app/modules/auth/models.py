from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', GUID(), ForeignKey('users.id'), primary_key=True),
    Column('role_id', GUID(), ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    roles = relationship("Role", secondary=user_roles, backref="users")
    customer = relationship("Customer", back_populates="user", uselist=False)
