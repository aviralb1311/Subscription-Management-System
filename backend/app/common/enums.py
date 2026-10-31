from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
