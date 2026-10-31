# Security Review

**Date:** 2026-10-31

## Checks
- JWT auth, RBAC enforced on backend
- Password hashing via bcrypt
- Customer ownership isolation
- Input validation via Pydantic
- SQL injection protected by SQLAlchemy ORM
- CORS configured
- No card/CVV stored
- Decimal used for financial values

## Recommendations
- Rate limiting recommended for production
- Secrets via environment variables only
