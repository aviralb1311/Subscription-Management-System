# ARCHITECTURE.md
*Modular Monolith Architecture*

## 1. Overview
Unified Subscription Intelligence & Revenue Management Platform built as a modular monolith with clear module boundaries.

## 2. Tech Stack
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Shadcn UI
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Database:** PostgreSQL 15+
- **Auth:** JWT access/refresh tokens
- **Background:** Celery, Redis (future phases)
- **Testing:** Pytest, Vitest

## 3. Module Structure

### Backend Modules
```
backend/app/
├── core/           # config, security, database, dependencies
├── common/         # utils, schemas, enums, constants
├── modules/        # business modules
│   ├── auth/
│   ├── users/
│   ├── products/
│   ├── plans/
│   ├── customers/
│   ├── quotations/
│   ├── subscriptions/
│   ├── invoices/
│   ├── payments/
│   ├── tax/
│   ├── discounts/
│   ├── renewals/
│   ├── analytics/
│   ├── notifications/
│   └── audit/
└── api/v1/         # route aggregation
```

### Frontend Structure
```
frontend/src/
├── components/     # UI components (shadcn)
├── lib/           # utils, api client, config
├── hooks/         # custom hooks
├── pages/         # page components
├── types/         # TypeScript types
└── utils/         # helpers
```

## 4. Core Principles
- Modular monolith - no microservices
- Business logic in services, not route handlers
- Configuration via environment variables
- No hardcoded secrets
- Financial operations in transactions
- Decimal for all monetary values
