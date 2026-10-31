# REQUIREMENTS.md
*Unified Subscription Intelligence & Revenue Management Platform*  
*Source: Master Prompt + PDF Documentation*  
*Status: Approved - Implementation Ready*

## 1. Functional Requirements

### 1.1 Authentication & User Management (P0)
- [FR-001] User registration with unique email validation
- [FR-002] Password validation (min 8 chars, uppercase, lowercase, special character)
- [FR-003] Secure password hashing
- [FR-004] Login/logout with JWT access and refresh tokens
- [FR-005] Password reset via email token
- [FR-006] Role-based access control (Admin, Staff, Customer)
- [FR-007] Admin-only staff account creation
- [FR-008] Role-appropriate permissions

### 1.2 Product Management (P0)
- [FR-009] Create/edit/deactivate products
- [FR-010] Product type, sales price, cost price, notes, descriptions
- [FR-011] Product variants with price adjustments
- [FR-012] Product availability/status

### 1.3 Plan & Pricing Management (P0)
- [FR-013] Plans for daily/weekly/monthly/yearly billing
- [FR-014] Flexible pricing, quantity management
- [FR-015] Plan versions for historical pricing
- [FR-016] Pause/resume/close/renew/expiry functionality

### 1.4 Quotation Management (P0)
- [FR-017] Create quotations with customer/product/plan selection
- [FR-018] Pricing calculations, discounts, taxes
- [FR-019] Quotation validity and status management
- [FR-020] Convert quotation to subscription

### 1.5 Subscription Management (P0)
- [FR-021] Subscription lifecycle with states: Draft, Quotation, Confirmed, Active, Paused, Closed, Renewal, Early Closure, Expiry, Cancellation, Past Due, Pending Cancellation
- [FR-022] Valid state transitions only
- [FR-023] Pause/resume/cancel/close/renew

### 1.6 Invoice & Billing (P0)
- [FR-024] Automatic invoice generation
- [FR-025] Invoice numbering, dates, line items
- [FR-026] Invoice states: Draft, Confirmed, Paid, Cancelled, Void
- [FR-027] Immutable invoice snapshots
- [FR-028] PDF generation

### 1.7 Tax, Discount & Payment (P0)
- [FR-029] Tax configuration and calculation
- [FR-030] Discounts/coupons with eligibility/limits
- [FR-031] Payment recording and allocation (partial/multiple)
- [FR-032] Payment reconciliation with CSV import
- [FR-033] Credit notes and refunds

### 1.8 Renewals, Notifications, Audit (P0)
- [FR-034] Automated renewals with grace periods
- [FR-035] Notifications
- [FR-036] Audit logs for sensitive actions
- [FR-037] Customer portal

### 1.9 Analytics (P0)
- [FR-038] MRR, ARR, churn, renewal rate, ARPU, LTV
- [FR-039] Revenue dashboards

## 2. Non-Functional Requirements

### 2.1 Performance (P0)
- [NFR-001] Important operations < 2s with thousands of subscriptions
- [NFR-002] Database indexes, pagination, no N+1 queries
- [NFR-003] Caching where appropriate, background processing

### 2.2 Security (P0)
- [NFR-004] Secure authentication and RBAC
- [NFR-005] Input validation, SQL injection prevention
- [NFR-006] Backend authorization, object-level isolation
- [NFR-007] JWT with rotation/revocation

### 2.3 Financial Correctness (P0)
- [NFR-008] Decimal for all monetary values
- [NFR-009] Historical snapshots, immutability
- [NFR-010] Transactions for financial operations
- [NFR-011] Idempotency
- [NFR-012] Valid state transitions

### 2.4 Architecture (P0)
- [NFR-013] Modular monolith
- [NFR-014] PostgreSQL database
- [NFR-015] React + FastAPI stack
