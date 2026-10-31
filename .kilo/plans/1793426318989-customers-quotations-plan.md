# PHASE 4 PLAN: Customers and Quotations

## Objective
Implement Customer management and Quotation workflow with pricing snapshots referencing specific product/plan versions.

## Branch
feat/customers-quotations (to be created from latest main)

## Requirements Review
From docs/planning/REQUIREMENTS.md:
- FR-017: Create quotations with customer/product/plan selection
- FR-018: Pricing calculations, discounts, taxes
- FR-019: Quotation validity and status management
- FR-020: Convert quotation to subscription
- Customer profiles mentioned

## Implementation Plan

### 1. Customer Management
**Models:**
- Customer (user_id FK to users, company_name, phone, billing_address JSONB, tax_id, status)

**Endpoints:**
- POST /api/v1/customers
- GET /api/v1/customers (paginated, Admin/Staff)
- GET /api/v1/customers/me
- GET/PUT /api/v1/customers/{id}
- Delete with rules

**RBAC:** Admin/Staff manage all, Customer manages own

### 2. Quotations
**Models:**
- Quotation (quotation_number, customer_id, status, valid_until, subtotal, discount_total, tax_total, total, currency, converted_to_subscription_id)
- QuotationLine (quotation_id, product_id, product_variant_id, plan_id, plan_version_id, description SNAPSHOT, quantity, unit_price SNAPSHOT, discount_amount, tax_amount, line_total)

**Critical:** Must reference plan_version_id and store price snapshots in quotation_lines

**States:** draft, sent, accepted, expired, cancelled, converted

**Endpoints:**
- POST /api/v1/quotations
- GET /api/v1/quotations (scoped by role)
- GET /api/v1/quotations/{id}
- PUT /api/v1/quotations/{id}
- POST /api/v1/quotations/{id}/send
- POST /api/v1/quotations/{id}/accept
- POST /api/v1/quotations/{id}/convert
- POST /api/v1/quotations/{id}/cancel

### 3. Business Rules
- Quotation must reference valid plan_version (current or specific)
- Line items store snapshots of prices
- Totals calculated server-side
- Validity period enforced
- Cannot convert expired quotations
- Conversion creates subscription (Phase 5) - just mark converted for now

### 4. Migrations
- customers table
- quotations, quotation_lines tables
- Foreign keys to users, products, plans, plan_versions

### 5. Tests
- Customer CRUD
- Quotation creation with version snapshots
- Pricing calculations
- State transitions
- Authorization

## Reusable Components
- Auth/RBAC from Phase 2
- Product/Plan/PlanVersion models from Phase 3
- Pagination patterns
- Service/router patterns

## Files to Create
Backend: modules/customers/, modules/quotations/
Migrations, tests, frontend components (if needed)

## Validation
- Quotations reference plan_version_id
- unit_price stored as snapshot (not just FK)
- Historical prices preserved
- No modification to existing Phase 1-3 code
